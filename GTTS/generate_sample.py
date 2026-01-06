#!/usr/bin/env python3
import pyttsx3
import os

out = os.path.join(os.path.dirname(__file__), "sample_speaker.wav")
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.save_to_file("Hello, this is a short sample voice used for testing voice cloning.", out)
engine.runAndWait()
print('sample created:', out)
