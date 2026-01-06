#!/usr/bin/env python3
# 🎭 COMBINED: XTTS Voice Cloning + BARK Emotion-Based TTS

import torch
# Monkeypatch torch.load for XTTS
_orig_torch_load = torch.load
def _load_wrapper(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _orig_torch_load(f, *args, **kwargs)
torch.load = _load_wrapper

from TTS.api import TTS
import bark
from bark import generate_audio, SAMPLE_RATE
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import pygame
import os
import time
import threading
import warnings
import numpy as np
import soundfile as sf
warnings.filterwarnings("ignore")

# Global variables
xtts_model = None
uploaded_voice = None
gpu_enabled = False

# ============== MAIN WINDOW ==============
window = Tk()
window.geometry('1100x900')
window.resizable(0, 0)
window.title("🎭 Voice Cloning + Emotion TTS (XTTS + Bark)")
window.config(bg='#0a0e27')

# Title
title = Label(window, text="🎭 XTTS Voice Cloning + Bark Emotion TTS", bg="#0a0e27", fg="#00D9FF", 
              font=('Helvetica', 24, 'bold'))
title.pack(pady=10)

# ============== NOTEBOOK (TABS) ==============
notebook = ttk.Notebook(window)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# ============== TAB 1: XTTS VOICE CLONING ==============
tab1 = Frame(notebook, bg="#1a1f3a")
notebook.add(tab1, text="🎤 XTTS Voice Cloning")

# Instruction
instr1 = Label(tab1, text="Upload your voice → Clone it → Apply emotion with DSP effects", 
              bg="#1a1f3a", fg="#00D9FF", font=('Helvetica', 11, 'bold'))
instr1.pack(pady=10)

# Text input
text_label1 = Label(tab1, text="📝 Text to synthesize:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
text_label1.pack()

text_input1 = Text(tab1, height=4, width=90, bg="#2d3561", fg="#FFFFFF", font=('Helvetica', 10), insertbackground='#00D9FF')
text_input1.pack(pady=5, padx=10)

# Emotion prompt
emotion_label1 = Label(tab1, text="😊 Emotion prompt (e.g., 'excited', 'sad', 'angry'):", bg="#1a1f3a", fg="#FFB6C1", font=('Helvetica', 10, 'bold'))
emotion_label1.pack()

emotion_input1 = Entry(tab1, width=90, bg="#2d3561", fg="#FFFFFF", font=('Helvetica', 10), insertbackground='#00D9FF')
emotion_input1.pack(pady=5, padx=10)

# Voice settings frame
settings1 = LabelFrame(tab1, text="⚙️ Settings", bg="#1a1f3a", fg="#00D9FF", font=('Helvetica', 10, 'bold'), padx=15, pady=10)
settings1.pack(pady=10, padx=10, fill="x")

# Language
lang_label1 = Label(settings1, text="Language:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
lang_label1.grid(row=0, column=0, sticky="w", pady=5)

lang_var1 = StringVar(value='en')
lang_dropdown1 = OptionMenu(settings1, lang_var1, 'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'ja', 'zh-cn')
lang_dropdown1.config(bg="#2d3561", fg="#00D9FF")
lang_dropdown1.grid(row=0, column=1, sticky="ew", pady=5, padx=10)

# Voice file
voice_label1 = Label(settings1, text="🎤 Voice Sample:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
voice_label1.grid(row=1, column=0, sticky="w", pady=5)

voice_file_label1 = Label(settings1, text="No file selected", bg="#2d3561", fg="#999999", font=('Helvetica', 9), padx=10, pady=5)
voice_file_label1.grid(row=1, column=1, sticky="ew", pady=5, padx=10)

def select_voice1():
    file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.mpeg *.wav *.ogg *.m4a *.mp4"), ("All Files", "*.*")])
    if file:
        global uploaded_voice
        uploaded_voice = file
        voice_file_label1.config(text=f"✓ {os.path.basename(file)}", fg="#00FF00")
        status1.config(text="Voice loaded! Ready to clone.", fg="#00FF00")

voice_btn1 = Button(settings1, text="📁 Load Voice", command=select_voice1, bg="#00D9FF", fg="#000000", font=('Helvetica', 9, 'bold'), padx=10)
voice_btn1.grid(row=1, column=2, padx=5, pady=5)

# Speed slider
speed_label1 = Label(settings1, text="Speed:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
speed_label1.grid(row=2, column=0, sticky="w", pady=5)

speed_var1 = DoubleVar(value=1.0)
speed_scale1 = Scale(settings1, from_=0.5, to=2.0, resolution=0.1, orient=HORIZONTAL, bg="#2d3561", fg="#00D9FF", length=200, variable=speed_var1)
speed_scale1.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5, padx=10)

# GPU toggle
gpu_label1 = Label(settings1, text="⚡ Use GPU:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
gpu_label1.grid(row=3, column=0, sticky="w", pady=5)

gpu_var1 = BooleanVar(value=torch.cuda.is_available())
gpu_check1 = Checkbutton(settings1, variable=gpu_var1, bg="#1a1f3a", fg="#FFFFFF", selectcolor="#2d3561")
gpu_check1.grid(row=3, column=1, sticky="w", pady=5, padx=10)

def apply_gpu1():
    use_gpu = bool(gpu_var1.get()) and torch.cuda.is_available()
    if bool(gpu_var1.get()) and not torch.cuda.is_available():
        messagebox.showwarning("GPU not available", "Using CPU instead.")
    threading.Thread(target=lambda: init_xtts(use_gpu), daemon=True).start()

apply_gpu_btn1 = Button(settings1, text="Apply", command=apply_gpu1, bg="#00D9FF", fg="#000000", font=('Helvetica', 9, 'bold'))
apply_gpu_btn1.grid(row=3, column=2, padx=5, pady=5)

# Emotion presets (for reference)
preset_label1 = Label(settings1, text="📊 DSP Effects (pitch/speed/energy):", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
preset_label1.grid(row=4, column=0, columnspan=3, sticky="w", pady=10)

pitch_label1 = Label(settings1, text="Pitch shift:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 9))
pitch_label1.grid(row=5, column=0, sticky="w", pady=5)

pitch_var1 = DoubleVar(value=0)
pitch_scale1 = Scale(settings1, from_=-12, to=12, resolution=1, orient=HORIZONTAL, bg="#2d3561", fg="#00D9FF", length=150, variable=pitch_var1)
pitch_scale1.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5, padx=10)

energy_label1 = Label(settings1, text="Energy:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 9))
energy_label1.grid(row=6, column=0, sticky="w", pady=5)

energy_var1 = DoubleVar(value=1.0)
energy_scale1 = Scale(settings1, from_=0.5, to=2.0, resolution=0.1, orient=HORIZONTAL, bg="#2d3561", fg="#00D9FF", length=150, variable=energy_var1)
energy_scale1.grid(row=6, column=1, columnspan=2, sticky="ew", pady=5, padx=10)

# Emotion keyword mapper function
emotion_map = {
    'happy|excited|joy|cheerful': {"pitch": 5, "energy": 1.4},
    'sad|sorrowful|melancholy|depressed': {"pitch": -4, "energy": 0.7},
    'angry|furious|mad|rage': {"pitch": 6, "energy": 1.5},
    'calm|peaceful|relax|sooth': {"pitch": -2, "energy": 0.8},
    'whisper|quiet|soft|gentle': {"pitch": -3, "energy": 0.6},
    'excited|enthusiastic|pumped': {"pitch": 7, "energy": 1.6},
}

def apply_emotion_from_prompt():
    """Auto-detect emotion keywords and adjust pitch/energy sliders"""
    emotion_text = emotion_input1.get().lower()
    
    detected = False
    for keywords, values in emotion_map.items():
        for keyword in keywords.split('|'):
            if keyword in emotion_text:
                pitch_var1.set(values["pitch"])
                energy_var1.set(values["energy"])
                status1.config(text=f"✓ Emotion detected: {keyword}! Adjusting sliders...", fg="#00FF00")
                detected = True
                break
        if detected:
            break
    
    if not detected:
        status1.config(text="⚠️ No emotion detected. Try: happy, sad, angry, calm, whisper, excited", fg="#FFA500")

apply_emotion_btn1 = Button(settings1, text="🎯 Apply Emotion", command=apply_emotion_from_prompt, bg="#FFD700", fg="#000000", font=('Helvetica', 9, 'bold'))
apply_emotion_btn1.grid(row=7, column=0, columnspan=3, sticky="ew", pady=5, padx=10)

# Status
status1 = Label(tab1, text="Ready", bg="#1a1f3a", fg="#00FF00", font=('Helvetica', 10, 'bold'))
status1.pack(pady=5)

# Buttons
btn_frame1 = Frame(tab1, bg="#1a1f3a")
btn_frame1.pack(pady=10)

def init_xtts(use_gpu):
    global xtts_model
    try:
        status1.config(text="Loading XTTS model...", fg="#FFA500")
        window.update()
        xtts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        status1.config(text="✓ Model ready", fg="#00FF00")
    except Exception as e:
        status1.config(text="❌ Model load failed", fg="#FF6B6B")
        messagebox.showerror("Error", str(e))

def generate_xtts():
    text = text_input1.get("1.0", END).strip()
    if not text:
        messagebox.showerror("Error", "Enter text!")
        return
    if not uploaded_voice:
        messagebox.showerror("Error", "Load a voice sample!")
        return
    
    try:
        status1.config(text="Generating speech (30-60 sec)...", fg="#FFA500")
        window.update()
        
        if xtts_model is None:
            use_gpu = bool(gpu_var1.get()) and torch.cuda.is_available()
            init_xtts(use_gpu)
            time.sleep(2)
        
        output_file = f"xtts_cloned_{int(time.time())}.wav"
        xtts_model.tts_to_file(text=text, file_path=output_file, speaker_wav=uploaded_voice, language=lang_var1.get(), speed=speed_var1.get())
        
        # Apply DSP effects if emotion is specified
        emotion = emotion_input1.get().lower()
        if emotion:
            try:
                y, sr = sf.read(output_file)
                if len(y.shape) > 1:
                    y = y[:, 0]  # Convert to mono
                
                # Time-stretch for pitch variation (simpler than pitch_shift)
                pitch_shift = pitch_var1.get()
                if pitch_shift != 0:
                    # Shift pitch by adjusting playback rate
                    # Positive shift = speed up (higher pitch), Negative = slow down (lower pitch)
                    shift_factor = 1.0 + (pitch_shift / 24.0)  # Map -12..12 to 0.5..1.5
                    shift_factor = np.clip(shift_factor, 0.5, 2.0)
                    indices = np.arange(len(y)) / shift_factor
                    indices = np.clip(indices, 0, len(y) - 1)
                    y = np.interp(indices, np.arange(len(y)), y)
                
                # Energy adjust
                energy_scale = energy_var1.get()
                if energy_scale != 1.0:
                    y = y * energy_scale
                
                # Clip to avoid distortion
                y = np.clip(y, -1.0, 1.0)
                sf.write(output_file, y.astype(np.float32), sr)
                status1.config(text="✓ DSP effects applied", fg="#00FF00")
            except Exception as dsp_err:
                status1.config(text="⚠️ DSP effects skipped, audio generated", fg="#FFA500")
        
        status1.config(text="✓ Generated! Playing...", fg="#00FF00")
        window.update()
        
        play_audio(output_file)
        
    except Exception as e:
        status1.config(text="❌ Error", fg="#FF6B6B")
        messagebox.showerror("Error", str(e))

play_btn1 = Button(btn_frame1, text="▶ Generate & Play (XTTS)", command=generate_xtts, bg="#00D9FF", fg="#000000", font=('Helvetica', 11, 'bold'), width=35, height=2)
play_btn1.pack(pady=5)

# ============== TAB 2: BARK EMOTION TTS ==============
tab2 = Frame(notebook, bg="#1a1f3a")
notebook.add(tab2, text="😊 Bark Emotion TTS")

# Instruction
instr2 = Label(tab2, text="Write text with emotion prompt → Bark generates with natural emotion", 
              bg="#1a1f3a", fg="#00D9FF", font=('Helvetica', 11, 'bold'))
instr2.pack(pady=10)

# Text input
text_label2 = Label(tab2, text="📝 Text with emotion tokens (e.g., 'I am so happy! [happy]'):", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
text_label2.pack()

text_input2 = Text(tab2, height=5, width=90, bg="#2d3561", fg="#FFFFFF", font=('Helvetica', 10), insertbackground='#00D9FF')
text_input2.insert("1.0", "Hello, I am so excited about this! [excited]")
text_input2.pack(pady=5, padx=10)

# Bark presets and speaker selection
settings2 = LabelFrame(tab2, text="⚙️ Bark Settings", bg="#1a1f3a", fg="#00D9FF", font=('Helvetica', 10, 'bold'), padx=15, pady=10)
settings2.pack(pady=10, padx=10, fill="x")

speaker_label2 = Label(settings2, text="Speaker Voice:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
speaker_label2.grid(row=0, column=0, sticky="w", pady=5)

# Bark speakers
bark_speakers = ['v2/en_speaker_1', 'v2/en_speaker_2', 'v2/en_speaker_3', 'v2/en_speaker_4', 'v2/en_speaker_5', 'v2/en_speaker_6']
speaker_var2 = StringVar(value=bark_speakers[0])
speaker_dropdown2 = OptionMenu(settings2, speaker_var2, *bark_speakers)
speaker_dropdown2.config(bg="#2d3561", fg="#00D9FF")
speaker_dropdown2.grid(row=0, column=1, sticky="ew", pady=5, padx=10)

# Language info
lang_info2 = Label(settings2, text="⚠️ Bark supports: EN (English), ES (Spanish), FR (French), DE (German), IT (Italian), PT (Portuguese), ZH (Chinese), JA (Japanese), KO (Korean)", bg="#1a1f3a", fg="#999999", font=('Helvetica', 8, 'italic'))
lang_info2.grid(row=1, column=0, columnspan=3, sticky="w", pady=5)

# Emotion tokens info
emotion_info2 = Label(settings2, text="📊 Emotion tokens: [happy] [sad] [excited] [calm] [angry] [whisper] [laughing] [crying]", bg="#1a1f3a", fg="#999999", font=('Helvetica', 8, 'italic'))
emotion_info2.grid(row=2, column=0, columnspan=3, sticky="w", pady=5)

# Quick button examples
quick_label2 = Label(settings2, text="📌 Quick prompts:", bg="#1a1f3a", fg="#FFFFFF", font=('Helvetica', 10, 'bold'))
quick_label2.grid(row=3, column=0, columnspan=3, sticky="w", pady=10)

def set_prompt(prompt):
    text_input2.delete("1.0", END)
    text_input2.insert("1.0", prompt)

quick_frame2 = Frame(settings2, bg="#1a1f3a")
quick_frame2.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)

quick_buttons = [
    ("😄 Happy", "Hello! I'm so happy! [happy]"),
    ("😢 Sad", "This is really sad... [sad]"),
    ("😠 Angry", "I'm really angry about this! [angry]"),
    ("😌 Calm", "Let me relax and think... [calm]"),
    ("🎉 Excited", "Wow, this is amazing! [excited]"),
    ("🤐 Whisper", "Listen carefully... [whisper]"),
]

for i, (btn_text, prompt) in enumerate(quick_buttons):
    btn = Button(quick_frame2, text=btn_text, command=lambda p=prompt: set_prompt(p), bg="#00D9FF", fg="#000000", font=('Helvetica', 8, 'bold'), width=15)
    btn.grid(row=0, column=i, padx=2, pady=2)

# Status
status2 = Label(tab2, text="Ready", bg="#1a1f3a", fg="#00FF00", font=('Helvetica', 10, 'bold'))
status2.pack(pady=5)

# Buttons
btn_frame2 = Frame(tab2, bg="#1a1f3a")
btn_frame2.pack(pady=10)

def generate_bark():
    text = text_input2.get("1.0", END).strip()
    if not text:
        messagebox.showerror("Error", "Enter text!")
        return
    
    try:
        status2.config(text="Generating with Bark (10-30 sec)...", fg="#FFA500")
        window.update()
        
        # Generate audio
        audio_array = generate_audio(text, history_prompt=speaker_var2.get())
        output_file = f"bark_emotion_{int(time.time())}.wav"
        
        # Save
        sf.write(output_file, audio_array, SAMPLE_RATE)
        
        status2.config(text="✓ Generated! Playing...", fg="#00FF00")
        window.update()
        
        play_audio(output_file)
        
    except Exception as e:
        status2.config(text="❌ Error", fg="#FF6B6B")
        messagebox.showerror("Error", str(e))

play_btn2 = Button(btn_frame2, text="▶ Generate & Play (Bark)", command=generate_bark, bg="#00D9FF", fg="#000000", font=('Helvetica', 11, 'bold'), width=35, height=2)
play_btn2.pack(pady=5)

# ============== UTILITY FUNCTIONS ==============
def play_audio(filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        messagebox.showerror("Playback Error", str(e))

# ============== FOOTER ==============
footer = Label(window, text="🎭 TAB 1: XTTS = Voice cloning with DSP effects | TAB 2: Bark = Native emotion support with tokens", bg="#0a0e27", fg="#888888", font=('Helvetica', 8, 'italic'))
footer.pack(pady=5)

# Run
window.mainloop()
