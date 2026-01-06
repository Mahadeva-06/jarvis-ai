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

base = os.path.dirname(__file__) if os.path.dirname(__file__) else os.getcwd()
voice_dir = os.path.join(os.path.dirname(base), 'voice')
user_voice = os.path.join(voice_dir, 'audio1.mp3')
output = os.path.join(base, 'cloned_from_user.wav')

print('Using user voice sample:', user_voice)
# Use CPU (gpu=False) unless you want to enable GPU
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
print('Model loaded')

text = "Hello. This is a test of the cloned voice from the provided audio sample."
tts.tts_to_file(text=text, file_path=output, speaker_wav=user_voice, language='en', speed=1.0)
print('Cloned output saved to:', output)
