# P300 Speller - Brain-Computer Interface Stimulator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.x-blue.svg)

## About the Project

This project presents a visual stimulation system for obtaining the P300 cerebral potential, which enables the construction of a Brain-Computer Interface (BCI) in the form of a virtual keyboard - the **P300 Speller**. 

### Why This Project Exists

The P300 Speller was developed to enable communication for individuals affected by neurodegenerative diseases that can lead to **locked-in syndrome** - a condition where the individual is unable to communicate or perform movements, except for eye movements. This interface provides an essential communication channel for those who have lost their motor abilities but retain cognitive function.

## How It Works

The P300 Speller consists of a virtual keyboard displayed as a 6x6 matrix on a screen. The paradigm works as follows:

1. **Matrix Display**: 36 characters are arranged in a 6x6 grid
2. **Row/Column Highlighting**: Rows and columns are sequentially highlighted
3. **User Focus**: The user fixes their gaze on the desired character
4. **Oddball Paradigm**: Of the 12 possible stimuli (6 rows + 6 columns), only two contain the target element
5. **P300 Detection**: The rare target stimulus evokes a P300 response, occurring approximately 300ms post-stimulus
6. **EEG Analysis**: Brain signals are captured via electroencephalogram (EEG) to detect the P300 potential

## Stimulation Models

The system implements three visual stimulation protocols:

### 1. **Oddball Classic**
- Traditional row/column intensification
- White characters on black background
- Standard P300 elicitation protocol

### 2. **Color Highlight**
- Similar to classic paradigm
- Highlights rows/columns by changing their color
- User-customizable highlight color
- May reduce visual fatigue

### 3. **Familiar Faces**
- Highlights by rapidly presenting images (typically familiar faces)
- Uses personal emotional connection to enhance P300 response
- Images displayed in the highlighted row/column

## Features

- ✅ **Three Stimulation Protocols**: Classic, Color Highlight, and Familiar Faces
- ✅ **Configurable Parameters**: Adjustable epochs, set time, and unset time
- ✅ **Training Mode**: For collecting training data and system calibration
- ✅ **Testing Mode**: Real-time BCI operation with character prediction
- ✅ **EEG Integration**: LSL (Lab Streaming Layer) support for EEG data collection
- ✅ **Visual Interface**: User-friendly GUI built with Tkinter
- ✅ **Marker Streaming**: Synchronized event markers for EEG analysis

## System Requirements

### Dependencies

```
python 3.x
tkinter
pylsl
PIL/Pillow
numpy
pandas
```

### Hardware

- EEG acquisition system compatible with LSL
- Display screen for stimulus presentation
- Computer capable of running Python applications

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/p300-speller.git
cd p300-speller
```

2. Install required dependencies:
```bash
pip install pylsl pillow numpy pandas
```

### Running the Application

```bash
python main.py
```

## Usage

### Training Mode

1. Select **Training Mode** from the menu
2. Configure the desired stimulation protocol
3. Enter the training text or subject name
4. Start the stimulation to collect training data
5. EEG data is recorded and synchronized with stimulus markers

### Testing Mode

1. Select **Testing Mode** from the menu
2. The system will use the trained classifier to predict characters
3. Focus on the desired character
4. The system detects P300 responses and predicts the intended character

### Configuration

Access the settings menu to adjust:
- **Number of Epochs**: Controls repetitions (1-15)
- **Set Time**: Duration of stimulus presentation (50-500ms)
- **Unset Time**: Inter-stimulus interval (50-500ms)

## Validation

The system was validated by:
1. Collecting EEG signals from volunteers during stimulation
2. Testing all three stimulation models
3. Recording spontaneous EEG (non-stimulation baseline)
4. Qualitative comparison of magnitude spectra between stimulation and baseline conditions

Results indicated significant changes in electroencephalographic activity, validating the system as **versatile for different experimental protocols in Cognitive Neuroscience**.

## Project Structure

```
MyStimulator/
├── main.py              # Main application and GUI
├── eeg_stream.py        # EEG streaming and LSL integration
├── connectEeg.py        # EEG connection utilities
├── Data/                # Data storage directory
├── Imagens/             # Images for Familiar Faces protocol
└── README.md            # This file
```

## Technical Details

- **Language**: Python
- **GUI Framework**: Tkinter
- **EEG Protocol**: Lab Streaming Layer (LSL)
- **Matrix Size**: 6x6 (36 characters)
- **Stimulus Types**: Row/Column highlighting
- **Event-Related Potential**: P300 (300ms post-stimulus)

## Applications

This system can be used for:
- 🧠 **Clinical Applications**: Communication aid for locked-in syndrome patients
- 🔬 **Research**: Cognitive neuroscience experiments
- 🎓 **Education**: BCI demonstrations and teaching
- 🧪 **Protocol Development**: Testing different P300 elicitation paradigms

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This work was developed as part of research in Brain-Computer Interfaces and Cognitive Neuroscience, aimed at improving quality of life for individuals with severe motor disabilities.

## Contact

For questions or collaborations, please open an issue on GitHub.

---

**Note**: This is an assistive technology project designed to help individuals with neurodegenerative diseases communicate. The system requires proper EEG equipment and should be used under appropriate supervision for medical applications.

