# Jarvis - AI Voice Assistant with Custom Voice

A lightweight, intelligent voice assistant with **custom cloned voice** for natural speech.

## 🎯 Architecture: 2-Stage Voice System

### Stage 1: Voice Cloning (One-Time)
```
Source Audio → XTTS → Voice Profile (brade_clone.wav)
```

### Stage 2: Voice Assistant (Runtime)
```
"Hello!" → Piper TTS + brade_clone.wav → Instant Audio
```

**Key Principle:** XTTS used ONCE for cloning. Piper (lightweight) for runtime.

See [ARCHITECTURE.md](../ARCHITECTURE.md) for complete design.

## ✨ Features

- 🎤 **Offline Speech-to-Text** - SpeechRecognition with PyAudio
- 🎙️ **Custom Voice** - Cloned with XTTS, runtime with Piper
- ⚡ **Fast** - No model loading delays at runtime
- 💻 **Laptop Control** - Browser, music, shutdown, etc.
- 🎨 **GUI** - Tkinter with dark theme
- 📦 **Modular** - Clean separation of concerns

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd jarvis
pip install -r requirements.txt
```

### 2. Clone a Voice (One-Time Setup)
```bash
# From project root
python VOICE_CLONING_STAGE1.py
# Creates: jarvis/voices/brade_clone.wav
```

### 3. Run Jarvis
```bash
python jarvis.py
```

That's it! Jarvis will introduce itself with your cloned voice.

## 📁 Project Structure

```
jarvis-ai/
├── jarvis/
│   ├── jarvis.py           # Main GUI & voice assistant
│   ├── tts.py              # Text-to-speech (Piper)
│   ├── stt.py              # Speech-to-text (SpeechRecognition)
│   ├── actions.py          # Command handlers
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Dependencies
│   ├── voices/
│   │   └── brade_clone.wav # Your cloned voice
│   └── README.md
│
├── VOICE_CLONING_STAGE1.py # Voice cloning (XTTS)
├── ARCHITECTURE.md         # Design documentation
└── requirements.txt        # All dependencies
```

## 🎙️ Voice Management

### Available Voices
Place any `.wav` file in `jarvis/voices/`:
```
jarvis/voices/
├── brade_clone.wav     # Default
├── narrator.wav        # Custom
└── commander.wav       # Custom
```

### Add New Voice
```bash
python VOICE_CLONING_STAGE1.py --source your_audio.mp3 --name your_voice
# Creates: jarvis/voices/your_voice.wav
```

### Switch Voice in GUI
Use the 🎙️ **Voices** menu button in Jarvis to select active voice.

## ⚙️ Configuration

Edit `config.py`:
```python
DEFAULT_VOICE = "jarvis/voices/brade_clone.wav"
TTS_LANGUAGE = 'en'
TTS_SPEED = 1.0
```

## 📚 Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **GUI** | Tkinter | User interface |
| **STT** | SpeechRecognition + PyAudio | Speech-to-text |
| **Voice Cloning** | XTTS (Coqui TTS) | Create voice profiles |
| **TTS** | Piper | Runtime speech synthesis |
| **Audio** | Pygame Mixer | Audio playback |

## 🔧 Modular Design

- **jarvis.py** - Orchestrator (GUI + coordination)
- **tts.py** - Text-to-speech (uses Piper + voice files)
- **stt.py** - Speech-to-text (SpeechRecognition)
- **actions.py** - Command execution
- **config.py** - Centralized settings

## 📝 Available Commands

- "open browser"
- "play music"
- "shutdown" / "restart"
- "take screenshot"
- "volume up" / "volume down"
- Custom voice input processing

## ⚡ Performance

| Metric | Value |
|--------|-------|
| **Startup** | <1 second |
| **First Response** | <1 second |
| **Consistent Speed** | <1 second per response |
| **Model Load** | None (voice is a file!) |

## 🐛 Troubleshooting

### Piper Not Found
```bash
pip install piper-tts
```

### Voice File Not Found
Make sure voice file exists:
```bash
ls jarvis/voices/
```

### Audio Playback Issues
```bash
pip install pygame
# Or reinstall: pip install --force-reinstall pygame
```

### Microphone Not Working
Check SpeechRecognition:
```bash
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_indexes())"
```

## 🎓 Learning Points

This project demonstrates:
1. **Clean Architecture** - Separation of voice cloning vs. runtime TTS
2. **Async Operations** - No GUI blocking
3. **Voice Synthesis** - Using pre-cloned voices for synthesis
4. **Modular Design** - Each component has single responsibility
5. **Python GUI** - Tkinter with threading

## 📄 License

MIT License

## 👤 Author

Jarvis AI Project  
Mahadeva-06

---

**See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed design documentation.**
