import time
import os
import string
import datetime
import threading
import PIL.Image
import PIL.ImageTk
from threading import Thread
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import Tk, Menu, colorchooser
from random import shuffle
from pylsl import StreamInfo, StreamOutlet, resolve_stream, StreamInlet
import tkinter as tk
from PIL import Image, ImageTk
import socket
import json
import pandas as pd
import pickle
import numpy as np
import statistics
import copy
import sys
from math import ceil
from math import floor as fl
from eeg_stream import receive_eeg_inlet
from eeg_stream import send_marker_outlet
import serial


skt = None

#ser = serial.Serial('COM7', 9600)  

voltage_mapping = {
    1: int(0.4 / 5 * 255),
    2: int(0.8 / 5 * 255),
    3: int(1.2 / 5 * 255),
    4: int(1.6 / 5 * 255),
    5: int(2.0 / 5 * 255),
    6: int(2.4 / 5 * 255),
    7: int(2.8 / 5 * 255),
    8: int(3.2 / 5 * 255),
    9: int(3.6 / 5 * 255),
    10: int(4.0 / 5 * 255),
    11: int(4.4 / 5 * 255),
    12: int(4.8 / 5 * 255),
}

###############Timing vars##################
Epoch = 6
curr_Epoch = 0
set_time = 150
unset_time = 100
sample_count = int(Epoch * (set_time + unset_time) / 2) * 12

############### GLOBAL VARIABLES ###################
start_simulation = False
trainMode = False
testMode = False
isSubjectMode = False
start_time_f = 0
start_time_ts = 0
stop_time_f = 0
stop_time_ts = 0
index = -1
preprocess = False

train_text = "P300"
subject_name = ""
filename = ""
classify = False
current_index = 0
inlet = None
outlet = None
eegFile = None
eeg_thread = None
threadList = []

ascii_value = 0
marker_list = {}
marker_dict = {}
timestamp = None
eeg_data = None
image_reference = None
image_path = None
############ Classifier #############
sampler_type = 0
dataset_type = 2
protocol_type = 1
font_color = None
#face_type = 0
#faces = ["P300Speller/Images/foto.png","P300Speller/Images/Ronaldinho.png","P300Speller/Images/Einstein.png"]
clf_type = 1

clf = []

path = os.path.join(os.getcwd(), 'Data')

baseline = None
baseline_data = None
# Fixed seed data
subject_train = ['O', 'I', '2', 'H', 'M', 'C', 'B', 'Q', 'S', '8', 'A', 'G', '7', 'Z', '4', 'L',
                 'Y', 'W', 'T', 'R', '6', 'F', 'K', '3', '0', 'X', 'J', 'U', 'D', 'V', '1', '5',
                 'E', '9', 'P', 'N']

# List to hold the random row and columns
List = []
for i in range(1, 13):
    List.append(i)
shuffle(List)
print(List)


############################################MENU Command Related Functions#####################################

####################### Training ################################
def do_training(isSubject):
    global trainMode, testMode

    if (start_simulation == True):
        messagebox.showwarning("Alerta", "Você não pode alterar modos no momento!")
        return
    global trainMode, isSubjectMode
    trainMode = True
    testMode = False
    isSubjectMode = isSubject
    if (isSubjectMode is True):
        pred_label1.configure(text="Nome do Participante")
        pred_Text.configure(state="normal")
        pred_Text.delete('1.0', END)

    else:
        pred_label1.configure(text="Texto Treino")
        pred_Text.configure(state="normal")
    pred_label2.configure(text="Caractere Treino")
    pred_label3.configure(text="")


####################### Testing ################################
def do_testing():
    global skt, sample_count, unset_time, set_time

    if (start_simulation == True):
        messagebox.showwarning("Alerta", "Você não pode alterar modos no momento!")
        return
    global trainMode, testMode
    trainMode = False
    testMode = True
    if skt is None:
        skt = socket.socket()
        skt.connect(('127.0.0.1', port))
        skt.send(str(sample_count).encode())
        temp = skt.recv(1024).decode()
        temp = int((set_time + unset_time) / 2)
        print(temp)
        skt.send(str(temp).encode())
        temp = skt.recv(1024).decode()
        skt.send(str(Epoch).encode())

    pred_label1.configure(text="Texto Previsto")
    if (pred_Text["state"] == "disabled"):
        pred_Text.configure(state="normal")
    pred_Text.delete('1.0', END)
    pred_Text.configure(state="disabled")
    pred_label2.configure(text="Caractere Previsto")
    pred_label3.configure(text="")


def choose_sampler(type):
    global sampler_type
    sampler_type = type
    print(f"Sampler_type: {type}")



def choose_protocol(type):
    global protocol_type, image_reference, image_path
    image_reference = None
    image_path = None
    protocol_type = type
    if protocol_type == 2:
        choose_color()
    elif protocol_type == 3:
        choose_face(type)
    print(f"Protocol_type: {type}")

def choose_color():
    global font_color
    color_tuple = colorchooser.askcolor(title="Escolha a cor de intensificação das letras")
    if color_tuple[1]:  # if user selected a color
        font_color = color_tuple[1]
        #print(f"Background color chosen: {font_color}")
        

def choose_face(value):
    global image_path
    if image_path is None:  # Familiar faces option and no image loaded yet
        image_path = filedialog.askopenfilename(title="Selecione a imagem", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])

def settings_update(case):
    global sample_count
    if (start_simulation == True):
        return
    if case == 1:
        global Epoch
        res = simpledialog.askinteger("INPUT", "Insira o número de Épocas", minvalue=1, maxvalue=15)
        if res is not None:
            Epoch = res
        print("Atualize: Épocas= {}".format(Epoch))
    elif case == 2:
        global set_time
        res = simpledialog.askinteger("INPUT", "Insira o set time em ms", minvalue=50, maxvalue=500)
        if res is not None:
            set_time = res
        print("Atualize: set_time= {}".format(set_time))
    elif case == 3:
        global unset_time
        res = simpledialog.askinteger("INPUT", "Insira o unset time em ms", minvalue=50, maxvalue=500)
        if res is not None:
            unset_time = res
        print("Atualize: unset_time= {}".format(unset_time))

    sample_count = int(Epoch * (set_time + unset_time) / 2) * 12


################# Sending Marker To server #######################
def create_marker_dict():
    global marker_dict, marker_list

    if testMode is True:
        marker_dict = {str(0): marker_list}

        serialized_dict = copy.deepcopy(marker_dict)
        print("Marker Dict")
        print(marker_dict)
        marker_list.clear()
        marker_dict.clear()
        print("Serialized Dict")
        print(serialized_dict)
        return serialized_dict



'''
Note:
index: 
 it is the index of the box under consideration

type:
    values =["CC","RBox"]
    CC->ColourChange 
    RBox-> Result Box
'''


def set(index, type):
    global set_time, ascii_value, box, protocol_type, image_reference, image_path, font_color

    font_size = 28
    font_type = 'Times New Roman'

    # Load the image if not loaded yet
    if image_reference is None and protocol_type == 3 and image_path:
        img = PIL.Image.open(image_path)
        img = img.resize((100, 100))  # Adjust the size as needed
        image_reference = PIL.ImageTk.PhotoImage(img)

    if type == 'CC':
        if index < 7:
            if protocol_type == 1:
                index1 = (index - 1) * 6 + 1
                for i in range(index1, index1 + 6):
                    box[i].config(fg="white", font=(font_type, font_size, 'bold'))
            elif protocol_type == 2:
                
                index1 = (index - 1) * 6 + 1
                for i in range(index1, index1 + 6):
                    box[i].config(fg=font_color, font=(font_type, font_size, 'bold'))
            elif protocol_type == 3:
                index1 = (index - 1) * 6 + 1
                for i in range(index1, index1 + 6):
                    box[i].config(image=image_reference)
                print("row: ", index)
        else:
            if protocol_type == 1:
                index1 = index - 6
                for i in range(index1, index1 + 31, 6):
                    box[i].config(fg="white", font=(font_type, font_size, 'bold'))
            elif protocol_type == 2:
                index1 = index - 6
                for i in range(index1, index1 + 31, 6):
                    box[i].config(fg=font_color, font=(font_type, font_size, 'bold'))
            elif protocol_type == 3:
                index1 = index - 6
                for i in range(index1, index1 + 31, 6):
                    box[i].config(image=image_reference)
                print("col: ", index1)
    elif type == "RBox":
        ascii_value = ord(str(box[index].cget('text'))[0])
        box[index].config(background="blue", font=(font_type, font_size, 'bold'))
        print("index received : {}".format(index))


def unset(index, type):
    global unset_time, trainMode, box, List
    font_size = 20
    font_type = 'Times New Roman'
    if (type == "CC"):
        if (index < 7):
            index1 = (index - 1) * 6 + 1
            for i in range(index1, index1 + 6):
                
                box[i].config(image= "",background="black",fg="grey", font=(font_type, font_size))
            print("row ", index, " returned")
        else:
            index1 = index - 6
            for i in range(index1, index1 + 31, 6):
                
                box[i].config(image= "",background="black", fg="grey", font=(font_type, font_size))
            print("col ", index1, " returned")

        # intensification delay!
        root.after(unset_time, send_marker, index)
    elif (type == "RBox"):
        box[index].config(image= "",background="black", font=(font_type, font_size))
        if trainMode:
            row = int((index - 1) / 6) + 1
            col = (index - 1) % 6 + 7
            shuffle(List)
            while abs(List.index(row) - List.index(col)) not in range(4, 8):
                shuffle(List)
            change_color(0)
        else:
            shuffle(List)


def result_display(row, col):
    global pred_Text, k_index, k_list
    global marker_dict, marker_list
    ind = (row - 1) * 6 + col - 6

    letter = str(box[ind].cget('text'))
    print(f'row :{row}, colum: {col} letter: {letter}')

    Text = pred_Text.get(1.0, "end-1c")
    Text += letter
    pred_Text.configure(state="normal")
    pred_Text.delete('1.0', END)
    
    pred_Text.insert(END, Text)
    pred_Text.configure(state="disabled")
    pred_label3.configure(text=letter)
    print("Row: {}, Column: {} value: {} ".format(row, col, letter))
    set(ind, "RBox")
    state_controller()
    marker_list.clear()
    marker_dict.clear()
    root.after(10000, unset, ind, "RBox")


############### For sending Marker to Server ###########################
def send_marker(index):
    global ascii_value, curr_Epoch

    timestamp = int(time.time() * 100)
    if testMode:
        marker_list[timestamp] = index
    else:
        vec = []
        if (ascii_value < 65):
            temp = ascii_value - 22
        else:
            temp = ascii_value - 65

        col = temp % 6 + 7
        row = fl(temp / 6) + 1
        curr_marker = index * 1000000 + (row + 10) * 10000 + (col + 10) * 100 + (curr_Epoch + 10)
        vec.append(curr_marker)
        outlet.push_sample(vec)

        #ser.write(voltage_mapping[index].to_bytes(1, byteorder='big'))
        print("Now sending marker: \t" + str(curr_marker) + "\n")

    # create_marker_dict()
    root.after(0, change_color, curr_Epoch)


####################################################################################


# current_epoch -> local parameter to check total epochs completed currently
def change_color(current_epoch):
    global start_simulation, index, Epoch, train_text, current_index
    global trainMode, curr_Epoch
    global set_time

    # marker_dict= {}

    if (start_simulation == False):
        return
    # if(index>=0):
    #     unset(List[index],"CC")
    index = (index + 1)
    if (index >= 12):
        current_epoch += 1
        index = 0
        # shuffle(List)
        if (current_epoch >= Epoch):
            if (trainMode is True):
                index = -1
                letter_trainer()
                return
            else:
                index = -1
                eeg_stream_controller(2)

                current_epoch = 0
                return

                # eeg_stream_controller("Start")
                # marker_dict = {0: marker_list}
                # serialized_dict = json.dumps(marker_dict)
                # skt.sendall(serialized_dict)

    set(List[index], "CC", )
    # intensification time
    curr_Epoch = current_epoch
    if (index >= 0):
        root.after(set_time, unset, List[index], "CC")

def letter_trainer():
    global current_index, train_text, subject_train, isSubjectMode, trainMode, preprocess, subject_name
    global start_simulation, filename
    if (start_simulation == False or trainMode == False):
        return
    if (isSubjectMode is True):
        subject_name = train_text

        if (current_index + 1 < len(subject_train)):
            current_index += 1
            letter = subject_train[current_index]
            pred_label3.configure(text=letter)
            if (letter.isalpha()):
                box_num = ord(letter) - ord('A') + 1
            elif (letter.isnumeric()):
                box_num = ord(letter) - ord('0') + 1 + 26
            else:
                box_num = 36
            # resultDisplay(0,ord(temp)-ord('A')+1)
            set(box_num, "RBox")
            root.after(5000, unset, box_num, "RBox")
        else:
            current_index = -1
            state_controller()
            
    else:
        if (current_index + 1 < len(train_text)):
            current_index += 1
            letter = train_text[current_index].upper()
            pred_label3.configure(text=letter)
            if (letter.isalpha()):
                box_num = ord(letter) - ord('A') + 1
            elif (letter.isnumeric()):
                box_num = ord(letter) - ord('0') + 1 + 26
            else:
                box_num = 36
            set(box_num, "RBox")
            root.after(5000, unset, box_num, "RBox")
        else:
            current_index = -1
            state_controller()
            
            

def update_time():
    global start_time_f, stop_time_f

    starttime.configure(text=start_time_f)
    stoptime.configure(text=stop_time_f)


def state_controller():
    global start_simulation, index, current_index, start_time_ts, start_time_f
    global stop_time_ts, stop_time_f, eeg_thread, testMode, trainMode, clf

    if testMode == True and len(clf) == 0:
        start_simulation = False
        messagebox.showinfo("Alerta", "Extensao nao disponivel!")
        return
    if (start_simulation == False):
        start_time_ts = time.time()
        start_time_f = time.strftime("%H:%M:%S %p")
        start_simulation = True
        button.configure(text='Parar')
    else:
        start_simulation = False
        stop_time_ts = time.time()
        stop_time_f = time.strftime("%H:%M:%S %p")
        update_time()
        if trainMode:
            unset(List[index], "CC")
        index = -1
        current_index = -1
        button.configure(text='Iniciar')


def start_speller():
    global start_simulation, index, start_time_ts, stop_time_ts, subject_name
    global start_time_f, stop_time_f
    global trainMode, train_text, current_index, port, skt

    if trainMode is False and testMode is False:
        messagebox.showinfo("Alerta", "Por favor, selecione um modo!")
        return
    train_text = pred_Text.get(1.0, "end-1c")

    if (trainMode is True and isSubjectMode is True and train_text is ""):
        messagebox.showinfo("Alerta", "Por favor, insira seu nome!")
    elif (trainMode is True and train_text is ""):
        messagebox.showinfo("Alerta", "Por favor, insira o texto para treino!")
    else:
        state_controller()

        if (trainMode is True):
            # auto-recovery from last letter before stopping.... do not update current_index then!
            current_index = -1
            # pred_label3.config(text=train_text[0].upper())
            letter_trainer()
        else:
            eeg_stream_controller(1)


################################ Main Program ####################################   

root = Tk()
root.state("zoomed")

menubar = Menu(root)
root.config(menu=menubar, bg="#666666")

############# FILE Menu #####################
filemenu = Menu(menubar, tearoff=0)
submenu = Menu(filemenu, tearoff=0)
menubar.add_cascade(label='Modo', menu=filemenu)
submenu.add_command(label='Modo Treino de Participante', command=lambda: do_training(True))
submenu.add_command(label='Modo Treino de Palavra', command=lambda: do_training(False))
filemenu.add_cascade(label="Modo Treino", menu=submenu, underline=0)
filemenu.add_command(label='Modo Teste', command=lambda: do_testing())
filemenu.add_separator()
filemenu.add_command(label='Sair', command=sys.exit)

############# MODEL Menu ###################

model = Menu(menubar, tearoff=0)
toggleVar = IntVar()

data_menu = Menu(model, tearoff=0)
tVar = IntVar()

data_menu.add_radiobutton(label='Combined', variable=tVar, value=1, command=lambda: choose_data(1))
data_menu.add_radiobutton(label='Session-wise', variable=tVar, value=2, command=lambda: choose_data(2))
data_menu.add_radiobutton(label='Subject-wise', variable=tVar, value=3, command=lambda: choose_data(3))


tVar2 = IntVar()
protocol_menu = Menu(model, tearoff=0)
protocol_menu.add_radiobutton(label='Oddball classic', variable=tVar2, value=1, command=lambda: choose_protocol(1))
protocol_menu.add_radiobutton(label='Color highlight', variable=tVar2, value=2, command=lambda: choose_protocol(2))
protocol_menu.add_radiobutton(label='Familiar faces', variable=tVar2, value=3, command=lambda: choose_protocol(3))

menubar.add_cascade(label='Modelo', menu=protocol_menu)

###############################################

######################Classifier Menu#######################

classifier = Menu(menubar, tearoff=0)
toggle = IntVar()
classifier.add_radiobutton(label='Saved Model', variable=toggle, value=3, command=lambda: check_classifier(0))
classifier.add_radiobutton(label='Neural Network', variable=toggle, value=1, command=lambda: check_classifier(1))
classifier.add_radiobutton(label='SVM', variable=toggle, value=2, command=lambda: check_classifier(2))


settings = Menu(menubar, tearoff=0)
settings.add_command(label="Epoch", command=lambda: settings_update(1))
settings.add_command(label="Set_time", command=lambda: settings_update(2))
settings.add_command(label="Unset_time", command=lambda: settings_update(3))
menubar.add_cascade(label='Configurações', menu=settings)

####################### Creating the CANVAS Structure #################################
box = dict()
import math

width = math.ceil(root.winfo_screenwidth() / 6)
height = math.ceil(root.winfo_screenheight() / 7.75)
roots = Canvas(root, height=6 * height, width=6 * width, bg="#666666", highlightthickness=0, bd=0)
frame = {}

##======================Creating the 6x6 Grid of P300 Speller=====================##
for r in range(1, 7):
    for c in range(1, 7):
        if (6 * (r - 1) + c <= 26):
            frame[6 * (r - 1) + c] = Frame(roots, width=width, height=height, bg="white")
            frame[6 * (r - 1) + c].pack_propagate(0)  # Stops child widgets of label_frame from resizing it
            box[6 * (r - 1) + c] = Label(frame[6 * (r - 1) + c], text=chr(64 + 6 * (r - 1) + c), borderwidth=0,
                                         background="black", width=width, height=height, fg="grey",
                                         font=("Courier", 19))
            box[6 * (r - 1) + c].pack(fill="both", expand=True, side='left')
            frame[6 * (r - 1) + c].place(x=(c - 1) * width, y=(r - 1) * height)

        else:
            frame[6 * (r - 1) + c] = Frame(roots, width=width, height=height, bg="white")
            frame[6 * (r - 1) + c].pack_propagate(0)
            box[6 * (r - 1) + c] = Label(frame[6 * (r - 1) + c], text=6 * (r - 1) + c - 27, borderwidth=0,
                                         background="black", width=width, height=height, fg="grey",
                                         font=("Courier", 19))
            box[6 * (r - 1) + c].pack(fill="both", expand=True, side='left')
            frame[6 * (r - 1) + c].place(x=(c - 1) * width, y=(r - 1) * height)

roots.pack(fill="both", expand=True)
##===============================================================================##

##========================Creating the Control Panel below the grid=======================##
root7 = Canvas(root, bg="#666666", highlightthickness=0, bd=0)

pred_label1 = Label(root7, text="Texto Previsto", fg="Black", font=("Times New Roman", 18), bg="#666666", width="18")
pred_label1.grid(row=0, column=0)

pred_Text = Text(root7, height=1, width=15, font=("Times New Roman", 18), state="disabled")
pred_Text.grid(row=1, column=0)

pred_label2 = Label(root7, text="Caractere Previsto", fg="Black", font=("Times New Roman", 18), bg="#666666", width="18",
                    padx="10")
pred_label2.grid(row=0, column=1)

pred_label3 = Label(root7, text="A", fg="Black", font=("Times New Roman", 18), bg="#666666", padx="10", pady="10")
pred_label3.grid(row=1, column=1)

button = Button(root7, text='Iniciar', width=10, height=1, fg="#666666", bg="#222222", font=("Times New Roman", 20),
                command=start_speller, activebackground="#666666", activeforeground="black")
button.grid(rowspan=2, row=0, column=2)

start_label = Label(root7, text='Tempo Inicial:', fg='black', font=("Times New Roman", 17), bg="#666666", padx="40")
start_label.grid(row=0, column=3)

starttime = Label(root7, text='00:00:00 00', fg='black', font=("Times New Roman", 17), bg="#666666", width="10")
starttime.grid(row=0, column=4)

stop_label = Label(root7, text='Tempo Final: ', fg='black', font=("Times New Roman", 17), bg="#666666", padx="40")
stop_label.grid(row=1, column=3)

stoptime = Label(root7, text='00:00:00 00', fg='black', font=("Times New Roman", 17), bg="#666666", width="10")
stoptime.grid(row=1, column=4)

root7.pack()

outlet = send_marker_outlet()
root.title("Estimulador Soletrador P300")
root.mainloop()
