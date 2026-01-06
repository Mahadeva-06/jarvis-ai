#!/usr/bin/env python3
import os
import torch
# Monkeypatch torch.load to allow full unpickling for trusted checkpoints
_orig_torch_load = torch.load
def _load_wrapper(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _orig_torch_load(f, *args, **kwargs)
torch.load = _load_wrapper

from TTS.api import TTS

base = os.path.dirname(__file__) or os.getcwd()
# project root is parent of GTTS folder
project_root = os.path.abspath(os.path.join(base, '..'))
voice_dir = os.path.join(project_root, 'voice')
user_voice = os.path.join(voice_dir, 'kakashi.mp3')
output = os.path.join(base, 'cloned_kakashi.wav')

# verify sample exists before loading model
if not os.path.isfile(user_voice):
    raise FileNotFoundError(f"Voice sample not found: {user_voice}")

print('Using user voice sample:', user_voice)
# Use CPU (gpu=False). Set gpu=True if you have a compatible GPU and drivers.
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
print('Model loaded')

text = "Hello. This is a cloned voice test generated from kakashi.mp3."
tts.tts_to_file(text=text, file_path=output, speaker_wav=user_voice, language='en', speed=1.0)
print('Cloned output saved to:', output)
