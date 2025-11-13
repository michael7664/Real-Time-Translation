# 🎧 Real-Time Italian to English Teams Meeting Translator

A Python-based real-time translator that converts Italian audio from Microsoft Teams meetings into English text with live display and automatic saving.

## 🌟 Overview

As a native English speaker living in Bologna, I created this tool to overcome language barriers in Italian work meetings. The application listens to Italian audio, translates it to English in real-time, and saves complete transcripts for future reference.

## ✨ Features

- **Real-time Translation**: Live Italian-to-English translation during Teams meetings
- **Audio Capture**: Automatic audio processing from system speakers
- **Live Display**: Real-time translation display with PyGame interface
- **Session Management**: One file per meeting with timestamps
- **Bilingual Saving**: Saves both original Italian and English translations
- **Smart Paragraphs**: Automatically groups related sentences

## 🛠 Tech Stack

- **Python 3.8+**
- **SpeechRecognition** - Audio processing and speech-to-text
- **Google Translate API** - Real-time translation
- **SoundDevice** - Cross-platform audio capture
- **PyGame** - Real-time display interface
- **NumPy** - Audio data processing

## 📋 Prerequisites

- Python 3.8 or higher
- macOS (tested on Apple Silicon) or Windows/Linux
- Microphone access permissions
- Internet connection (for speech recognition and translation)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/michael7664/Real-Time-Translation.git
cd teams-italian-translator