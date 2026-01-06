# Jarvis - AI Voice Assistant

A lightweight, offline-capable voice assistant for laptop control.

## Features

- 🎤 Offline Speech-to-Text recognition
- 🎯 Voice command processing
- 💻 Laptop control commands
- ⚙️ Modular and extensible architecture

## Project Structure

```
├── main.py              # Entry point
├── stt.py               # Offline speech-to-text
├── actions.py           # Laptop control commands
├── config.py            # Settings
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Installation

1. Clone or navigate to the project directory
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

Speak commands to control your system. Available commands:
- "open browser"
- "play music"
- "shutdown"
- "restart"
- "take screenshot"

## Requirements

- Python 3.7+
- Microphone for speech input
- Internet connection (for cloud-based speech recognition)

## License

MIT License

## Author

Jarvis AI Project
