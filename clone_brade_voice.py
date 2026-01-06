#!/usr/bin/env python3
"""
Clone brade(man) voice for Jarvis
Creates a pre-cloned voice file that Jarvis can use
"""

import torch
import warnings
import os

warnings.filterwarnings("ignore")

# Monkeypatch torch.load
_orig_torch_load = torch.load
def _load_wrapper(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _orig_torch_load(f, *args, **kwargs)
torch.load = _load_wrapper

from TTS.api import TTS

print("[CLONING] Starting voice cloning for brade(man)...")

# Paths
source_voice = "/home/malla/Downloads/jarvis-ai/voice/brade(man).mp3"
output_voice = "/home/malla/Downloads/jarvis-ai/jarvis/voices/brade_voice.wav"

# Check if source exists
if not os.path.exists(source_voice):
    print(f"[ERROR] Source voice not found: {source_voice}")
    exit(1)

print(f"[CLONING] Source: {source_voice}")
print(f"[CLONING] Output: {output_voice}")

# Initialize XTTS
print("[CLONING] Loading XTTS v2 model (this may take 1-2 minutes)...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
print("[CLONING] Model loaded!")

# Clone the voice
text = "Hello, I am brade, your new voice. I am ready to assist you with anything you need."
print("[CLONING] Cloning voice (this may take 30-60 seconds)...")

try:
    tts.tts_to_file(
        text=text,
        file_path=output_voice,
        speaker_wav=source_voice,
        language='en',
        speed=1.0
    )
    print(f"[SUCCESS] Voice cloned and saved to: {output_voice}")
    print("[SUCCESS] Jarvis will now use the brade voice!")
except Exception as e:
    print(f"[ERROR] Voice cloning failed: {e}")
    exit(1)
