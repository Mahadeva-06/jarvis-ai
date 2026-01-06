#!/usr/bin/env python3
#!/usr/bin/env python3
# Voice Cloning Text to Speech using XTTS (Coqui TTS)

import torch
# Monkeypatch torch.load to allow full unpickling for trusted checkpoints (same workaround as other clone scripts)
_orig_torch_load = torch.load
def _load_wrapper(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _orig_torch_load(f, *args, **kwargs)
torch.load = _load_wrapper

from TTS.api import TTS
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import pygame
import os
import time
import threading
import warnings
warnings.filterwarnings("ignore")

# Defer TTS model initialization so we can choose GPU/CPU at runtime
tts = None
gpu_enabled = False

# Create Window
window = Tk()
window.geometry('900x750')
window.resizable(0, 0)
window.title("Advanced Voice Cloning - XTTS")
window.config(bg='#1a1a1a')

# Title
title = Label(window, text="Voice Cloning Text-to-Speech", bg="#1a1a1a", fg="#FF1493", 
              font=('Helvetica', 28, 'bold'))
title.pack(pady=15)

# Variables
uploaded_voice = None
voice_name_var = StringVar(value="Default Voice")

# Text Input Area
instruction = Label(window, text="Enter text to convert to speech:", 
                    bg="#1a1a1a", fg="#FFFFFF", font=('Helvetica', 11))
instruction.pack()

text_input = Text(window, height=6, width=70, bg="#333333", fg="#FFFFFF", 
                  font=('Helvetica', 11), insertbackground='#FF1493')
text_input.pack(pady=10, padx=20)

# Voice Settings Frame
settings_frame = LabelFrame(window, text="Voice Settings", bg="#1a1a1a", fg="#FF1493", 
                           font=('Helvetica', 10, 'bold'), padx=15, pady=10)
settings_frame.pack(pady=10, padx=20, fill="x")

# Language Selection
lang_label = Label(settings_frame, text="Language:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
lang_label.grid(row=0, column=0, sticky="w", pady=5)

lang_var = StringVar(value='en')
lang_dropdown = OptionMenu(settings_frame, lang_var, 'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'ja', 'zh-cn')
lang_dropdown.config(bg="#333333", fg="#FF1493", activebackground="#555555", activeforeground="#FF1493")
lang_dropdown.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))

# Voice File Selection
voice_label = Label(settings_frame, text="Voice Sample:", bg="#1a1a1a", fg="#FFFFFF", 
                    font=('Helvetica', 10, 'bold'))
voice_label.grid(row=1, column=0, sticky="w", pady=5)

voice_file_label = Label(settings_frame, text="No file selected", bg="#444444", fg="#999999", 
                         font=('Helvetica', 9), padx=10, pady=5)
voice_file_label.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))

def select_voice_file():
    file = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.mp3 *.mpeg *.wav *.ogg *.m4a *.mp4"), ("All Files", "*.*")]
    )
    if file:
        global uploaded_voice
        uploaded_voice = file
        voice_name_var.set(os.path.basename(file))
        voice_file_label.config(text=f"✓ {os.path.basename(file)}", fg="#00FF00")
        status_label.config(text="Voice sample loaded! Ready to clone.", fg="#00FF00")

select_voice_btn = Button(settings_frame, text="📁 Load Voice", command=select_voice_file, 
                         bg="#FF1493", fg="white", font=('Helvetica', 9, 'bold'), 
                         padx=10, pady=2)
select_voice_btn.grid(row=1, column=2, padx=5, pady=5)

# Speaker Name
name_label = Label(settings_frame, text="Speaker Name:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
name_label.grid(row=2, column=0, sticky="w", pady=5)

name_entry = Entry(settings_frame, width=30, bg="#444444", fg="#FFFFFF", 
                   font=('Helvetica', 10), insertbackground='#FF1493')
name_entry.insert(0, "My Voice")
name_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

# Speed Control
speed_label = Label(settings_frame, text="Speed:", bg="#1a1a1a", fg="#FFFFFF", 
                    font=('Helvetica', 10, 'bold'))
speed_label.grid(row=3, column=0, sticky="w", pady=5)

speed_var = IntVar(value=1)
speed_scale = Scale(settings_frame, from_=50, to=200, orient=HORIZONTAL, 
                   bg="#333333", fg="#FF1493", length=200, variable=speed_var)
speed_scale.grid(row=3, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

# GPU Selection (will reinitialize the model when applied)
gpu_label2 = Label(settings_frame, text="Use GPU if available:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
gpu_label2.grid(row=4, column=0, sticky="w", pady=5)

gpu_var = BooleanVar(value=torch.cuda.is_available())
gpu_check = Checkbutton(settings_frame, variable=gpu_var, bg="#1a1a1a", fg="#FFFFFF", selectcolor="#333333")
gpu_check.grid(row=4, column=1, sticky="w", pady=5, padx=(10,0))

apply_gpu_btn = Button(settings_frame, text="Apply GPU", command=lambda: None, bg="#2E8B57", fg="white", font=('Helvetica', 9, 'bold'))
apply_gpu_btn.grid(row=4, column=2, padx=5, pady=5)

def init_tts(use_gpu: bool):
    """Initialize or reinitialize the TTS model. Runs in background to avoid blocking UI."""
    global tts, gpu_enabled
    try:
        status_label.config(text="Loading XTTS model (this may take a minute)...", fg="#FFA500")
    except Exception:
        pass
    try:
        # create/replace TTS instance
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        gpu_enabled = use_gpu
        try:
            status_label.config(text=f"Model ready (GPU={'yes' if gpu_enabled else 'no'})", fg="#00FF00")
        except Exception:
            pass
    except Exception as e:
        try:
            status_label.config(text="Model load failed", fg="#FF6B6B")
        except Exception:
            pass
        messagebox.showerror("Model Error", f"Failed to load TTS model: {e}")

def apply_gpu_setting():
    # Reinitialize model in a background thread
    use_gpu = bool(gpu_var.get()) and torch.cuda.is_available()
    if bool(gpu_var.get()) and not torch.cuda.is_available():
        messagebox.showwarning("GPU not available", "GPU checkbox selected but no CUDA device detected. Using CPU instead.")
    threading.Thread(target=init_tts, args=(use_gpu,), daemon=True).start()

# Wire the Apply button command now that the handler exists
try:
    apply_gpu_btn.config(command=apply_gpu_setting)
except Exception:
    pass


# Status Label
status_label = Label(window, text="Ready", bg="#1a1a1a", fg="#00FF00", 
                     font=('Helvetica', 10, 'bold'))
status_label.pack(pady=5)

# Function to play audio
def play_audio(filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        status_label.config(text="✓ Playback completed!", fg="#00FF00")
    except Exception as e:
        messagebox.showerror("Playback Error", str(e))
        status_label.config(text="❌ Playback error", fg="#FF6B6B")

# Function to convert with cloned voice
def convert_with_clone():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    if not uploaded_voice:
        messagebox.showerror("Error", "Please select a voice sample first!")
        return
    
    try:
        status_label.config(text="Generating speech with your cloned voice... (30-60 sec)", fg="#FFA500")
        window.update()
        
        # ensure model initialized with requested device
        if tts is None:
            # initialize synchronously so generation can proceed
            use_gpu = bool(gpu_var.get()) and torch.cuda.is_available()
            init_tts(use_gpu)

        lang = lang_var.get()
        speaker_name = name_entry.get() or "Cloned Voice"
        speed = speed_var.get() / 100.0
        
        # Generate speech with voice cloning
        output_file = f"cloned_{int(time.time())}.wav"
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            speaker_wav=uploaded_voice,
            language=lang,
            speed=speed
        )
        
        status_label.config(text="✓ Speech generated! Playing...", fg="#00FF00")
        window.update()
        
        time.sleep(1)
        play_audio(output_file)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="❌ Error occurred", fg="#FF6B6B")

# Function to save cloned speech
def save_cloned_speech():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    if not uploaded_voice:
        messagebox.showerror("Error", "Please select a voice sample first!")
        return
    
    try:
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", 
                                                  filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")])
        if save_path:
            status_label.config(text="Generating and saving... (30-60 sec)", fg="#FFA500")
            window.update()
            
            # ensure model initialized
            if tts is None:
                use_gpu = bool(gpu_var.get()) and torch.cuda.is_available()
                init_tts(use_gpu)

            lang = lang_var.get()
            speed = speed_var.get() / 100.0
            
            tts.tts_to_file(
                text=text,
                file_path=save_path,
                speaker_wav=uploaded_voice,
                language=lang,
                speed=speed
            )
            
            messagebox.showinfo("Success", f"Audio saved to:\n{save_path}")
            status_label.config(text="✓ File saved successfully!", fg="#00FF00")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="❌ Save failed", fg="#FF6B6B")

# Function to clear
def clear_all():
    global uploaded_voice
    text_input.delete("1.0", END)
    uploaded_voice = None
    voice_file_label.config(text="No file selected", fg="#999999")
    name_entry.delete(0, END)
    name_entry.insert(0, "My Voice")
    status_label.config(text="Ready", fg="#00FF00")

# Buttons Frame
button_frame = Frame(window, bg="#1a1a1a")
button_frame.pack(pady=15)

play_btn = Button(button_frame, text="▶ Generate & Play", command=convert_with_clone, 
                  bg="#FF1493", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=20, height=2, activebackground="#E60F8C")
play_btn.grid(row=0, column=0, padx=5)

save_btn = Button(button_frame, text="💾 Save Audio", command=save_cloned_speech, 
                  bg="#1E90FF", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=20, height=2, activebackground="#1873DA")
save_btn.grid(row=0, column=1, padx=5)

clear_btn = Button(button_frame, text="🗑 Clear All", command=clear_all, 
                   bg="#FF6B6B", fg="white", font=('Helvetica', 11, 'bold'), 
                   width=20, height=2, activebackground="#E60F0F")
clear_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Info Label
info_label = Label(window, text="Powered by XTTS v2 (Coqui) | Clone your voice or others | 9 Languages Supported | First generation takes longer", 
                   bg="#1a1a1a", fg="#999999", font=('Helvetica', 8, 'italic'))
info_label.pack(pady=5)

# Run the window
window.mainloop()
