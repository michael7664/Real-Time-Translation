# Real-Time Audio Translator 🎤🌐

A sophisticated real-time audio translation application with GUI interface that captures audio, converts speech to text, and translates between multiple languages instantly.

![Real-Time Translation](https://img.shields.io/badge/Real--Time-Translation-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Qt](https://img.shields.io/badge/Qt-6.0%2B-orange)
![Multi-Language](https://img.shields.io/badge/Multi--Language-12%2B-yellow)

## ✨ Features

- **Real-time Audio Capture**: Continuous microphone monitoring
- **Multi-language Support**: 12+ source and target languages
- **Intelligent GUI**: Modern Qt-based interface with system tray integration
- **Smart Paragraph Detection**: Automatically organizes translations into paragraphs
- **Custom Output Folders**: Choose where to save translation files
- **Live Preview**: Real-time display of recognized and translated text
- **Background Operation**: Minimize to system tray
- **Fast Speech Optimization**: Enhanced detection for rapid speech

## 🗣️ Supported Languages

**Source Languages**: Italian, Spanish, French, German, Chinese, Japanese, Korean, Russian, Portuguese, Arabic, Hindi

**Target Languages**: English, Spanish, French, German, Italian, Chinese, Japanese, Korean, Russian

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Qt6 Development Tools**
- **CMake 3.16+**

### Installation

#### macOS
```bash
# Install Qt6
brew install qt6

# Install Python dependencies
pip install -r requirements.txt

# Install system audio dependencies
brew install portaudio

#### Windows
Install Python 3.8+
Install Qt6
Install CMake
Run in Command Prompt: pip install -r requirements.txt


### Ubuntu/Debian
# Install Qt6 and development tools
sudo apt update
sudo apt install qt6-base-dev cmake build-essential

# Install Python and dependencies
sudo apt install python3 python3-pip
pip3 install -r requirements.txt

# Install audio dependencies
sudo apt install portaudio19-dev python3-pyaudio



#### Building the Application
pip install -r requirements.txt
# Clone the repository
git clone https://github.com/michael7664/Real-Time-Translation.git
cd Real-Time-Translation

# Create build directory
mkdir build && cd build

# Configure with CMake
cmake ..

# Build the application
make

#On Windows use:
cmake --build .


### Running the Application
Go to gui/build
double click on RealTimeTranslatorGUI

or

from terminl
cd build
./RealTimeTranslatorGUI






### USER MANUAL
Basic Usage

Launch the Application: Run RealTimeTranslatorGUI from the build directory
Select Languages: Choose source and target languages from dropdown menus
Choose Output Folder (Optional): Click "Choose Folder" to select where translation files are saved
Start Translation: Click "Start Translation" to begin audio capture
Speak: Talk in the source language - translations appear in real-time
Monitor: Watch the live output panel for recognized text and translations
Stop: Click "Stop Translation" when finished
Advanced Features

Custom Output Locations

Click "Choose Folder" to select a custom directory for translation files
If no folder selected, files are saved to ~/output/
Files are automatically named with timestamps: translations_YYYYMMDD_HHMMSS.txt
System Tray Integration

Minimize the window to keep translation running in background
Double-click tray icon to show/hide the main window
Right-click tray icon for quick actions (Show/Hide/Quit)
Paragraph Detection

Automatically groups translations into paragraphs based on timing
New paragraph starts after 15 seconds of silence
Complete sentences are organized into bullet points
File Output Format

Translation files include:

Timestamped entries for each translation
Paragraph organization with visual separators
Session summaries with statistics
Both source and translated text
Example output:

text
══════════════════════════════════════════════
PARAGRAPH 1 START: 14:30:25
══════════════════════════════════════════════
[14:30:25]
ITALIAN: Ciao, come stai?
ENGLISH: Hello, how are you?
----------------------------------------
🛠️ Technical Details

Architecture

Frontend: Qt6 C++ GUI application
Backend: Python real-time audio processing
Communication: Inter-process communication (QProcess)
Speech Recognition: Google Speech Recognition API
Translation: Google Translate API
Key Components

MainWindow: Primary GUI interface
StandaloneTranslator: Core translation engine
SpeechToText: Audio processing and recognition
TextTranslator: Language translation services
Performance Optimizations

Fast speech detection algorithms
Adaptive audio buffer management
Real-time processing pipelines
Efficient memory usage
🔧 Troubleshooting

Common Issues

No Audio Detected

Check microphone permissions
Ensure default audio input is set correctly
Test with system audio recorder
Poor Recognition Quality

Speak clearly at natural pace
Reduce background noise
Ensure good microphone quality
Build Errors

Verify Qt6 installation
Check CMake version compatibility
Ensure all dependencies are installed
Python Import Errors

Run pip install -r requirements.txt
Check Python version (3.8+ required)
Debug Mode

Enable verbose logging by checking the output panel in the GUI for detailed status messages.

🤝 Contributing

We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features.

Development Setup

Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit a pull request
📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

Google Speech Recognition API
Google Translate API
Qt Framework for cross-platform GUI
SoundDevice for audio capture
📞 Support

If you encounter any issues or have questions:

Check the troubleshooting section above
Search existing GitHub issues
Create a new issue with detailed information