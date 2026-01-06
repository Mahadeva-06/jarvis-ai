# Jarvis Voice Setup Guide

## How Voice Cloning Works in Jarvis

### ❌ **Wrong Approach (What we were doing):**
```
User clicks "Speak" → Clone voice (30-60 sec) → Generate speech → Play
User clicks "Speak" again → Clone voice AGAIN (30-60 sec) → Generate speech → Play
```
This is slow and inefficient!

### ✅ **Correct Approach (What we do now):**
```
Step 1: PRE-CLONE (Once, manually)
- Take a voice sample (5-10 sec audio)
- Clone it using XTTS → Generates cloned_voice.wav (30-60 sec)
- Save as: jarvis/voices/jarvis_voice.wav

Step 2: USE PRE-CLONED VOICE (Fast, Instant)
User clicks "Speak" → Use jarvis_voice.wav as reference → Generate speech (5-10 sec) → Play
User clicks "Speak" again → Use jarvis_voice.wav as reference → Generate speech (5-10 sec) → Play
```

## Current Pre-Cloned Voices Available

1. **jarvis_voice.wav** - Kakashi's voice clone (Default)
   - Pre-cloned from: `GTTS/kakashi.mp3`
   - Fast, natural, male voice

2. **user_voice.wav** - Your voice clone
   - Pre-cloned from: `GTTS/cloned_from_user.wav`
   - Personalized voice

## How to Add Your Own Cloned Voice

### Option 1: Use GTTS Voice Cloning App
```bash
cd /home/malla/Downloads/jarvis-ai/GTTS
python3 voice_cloning_app.py
```
1. Load a voice sample (.wav, .mp3)
2. Click "▶ Generate & Play" to clone it
3. Click "💾 Save Audio" and save as: `jarvis/voices/your_voice_name.wav`

### Option 2: Manual Cloning Script
Create a cloning script:
```python
from TTS.api import TTS

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# First cloning (takes 30-60 sec)
tts.tts_to_file(
    text="Hello, I am your cloned voice",
    file_path="jarvis/voices/my_voice.wav",
    speaker_wav="path/to/voice_sample.mp3",  # 5-10 sec sample
    language='en',
    speed=1.0
)
```

## Speed Comparison

| Operation | Time | Frequency |
|-----------|------|-----------|
| Clone voice (one-time) | 30-60 sec | Once per voice |
| Generate speech with cloned voice | 5-10 sec | Every time Jarvis speaks |
| Play audio | Real-time | Every time Jarvis speaks |

## Technical Details

- **XTTS Model**: `tts_models/multilingual/multi-dataset/xtts_v2`
- **Voice Reference**: The `.wav` file is used as a style reference, not cloned again
- **Support**: 9+ languages
- **GPU**: Optional but recommended (10x faster)

## Files Location

```
jarvis/
├── voices/
│   ├── jarvis_voice.wav      # Default pre-cloned voice
│   ├── user_voice.wav        # User's pre-cloned voice
│   └── your_voice.wav        # Add more voices here
├── tts.py                     # TTS module (handles synthesis, NOT cloning)
├── jarvis.py                  # GUI with voice menu
└── config.py                  # Configuration
```

## Troubleshooting

**Q: Jarvis takes 30-60 seconds to speak?**
A: Check if you're using a raw voice sample instead of a pre-cloned voice. Use pre-cloned `.wav` files from the `voices/` directory.

**Q: How do I know if a voice is pre-cloned?**
A: Pre-cloned voices should be in `jarvis/voices/` directory as `.wav` files.

**Q: Can I use the same voice sample file multiple times?**
A: Yes, once cloned and saved, reuse the cloned `.wav` file. Don't clone the same file again.
