import mne
import matplotlib.pyplot as plt
import numpy as np
import socket

def process_data(data):
    # Convert the data from bytes to a string
    data_str = data.decode('utf-8')

    # Split the string into a list of strings
    data_list = data_str.split(',')

    # Convert the list of strings into a list of floats
    data_floats = [float(x) for x in data_list]

    # Convert the list of floats into a numpy array
    processed_data = np.array(data_floats)

    return processed_data

# Create a socket object for UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP and port
# Replace 'your_local_ip_address' with your computer's local IP address
# Replace 'device_port' with the port number for your device
s.bind(('192.168.1.4', 11111))

# Create a plot
fig, ax = plt.subplots()

# Continuously collect and plot data
while True:
    # Receive data from the device
    data, addr = s.recvfrom(1024)

    # Process the data into a numpy array
    data = process_data(data)

    # Create a Raw object from the data
    info = mne.create_info(ch_names=['EEG'], sfreq=256, ch_types=['eeg'])
    raw = mne.io.RawArray([data], info)

    # Plot the data
    raw.plot(duration=5, n_channels=1, scalings='auto', color='b', show=False)

    # Update the plot
    plt.draw()
    plt.pause(0.01)

# Close the connection
s.close()