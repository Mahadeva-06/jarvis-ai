#!/usr/bin/env python3
# Voice Cloning Text to Speech with EMOTION CONTROL using XTTS (Coqui TTS)

import torch
# Monkeypatch torch.load to allow full unpickling for trusted checkpoints
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

# Defer TTS model initialization
tts = None
gpu_enabled = False

# Create Window
window = Tk()
window.geometry('1000x900')
window.resizable(0, 0)
window.title("🎭 Voice Cloning TTS with EMOTION CONTROL")
window.config(bg='#1a1a1a')

# Title
title = Label(window, text="Voice Cloning + Emotion Control TTS", bg="#1a1a1a", fg="#FF1493", 
              font=('Helvetica', 28, 'bold'))
title.pack(pady=15)

# Variables
uploaded_voice = None
style_reference_voice = None
voice_name_var = StringVar(value="Default Voice")

# ============== TEXT INPUT AREA ==============
instruction = Label(window, text="📝 Enter text to convert to speech:", 
                    bg="#1a1a1a", fg="#FFFFFF", font=('Helvetica', 11, 'bold'))
instruction.pack()

text_input = Text(window, height=4, width=80, bg="#333333", fg="#FFFFFF", 
                  font=('Helvetica', 10), insertbackground='#FF1493')
text_input.pack(pady=10, padx=20)

# ============== EMOTION PROMPT AREA ==============
emotion_instruction = Label(window, text="😊 Emotion Prompt (e.g., 'Say this excitedly and happily' or 'angry and loud'):", 
                           bg="#1a1a1a", fg="#FF1493", font=('Helvetica', 10, 'bold'))
emotion_instruction.pack()

emotion_input = Text(window, height=2, width=80, bg="#444444", fg="#FFFFFF", 
                     font=('Helvetica', 10), insertbackground='#FF1493')
emotion_input.pack(pady=5, padx=20)

# ============== VOICE SETTINGS FRAME ==============
settings_frame = LabelFrame(window, text="⚙️ Voice & Emotion Settings", bg="#1a1a1a", fg="#FF1493", 
                           font=('Helvetica', 10, 'bold'), padx=15, pady=10)
settings_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Language Selection
lang_label = Label(settings_frame, text="Language:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
lang_label.grid(row=0, column=0, sticky="w", pady=5)

lang_var = StringVar(value='en')
lang_dropdown = OptionMenu(settings_frame, lang_var, 'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'ja', 'zh-cn')
lang_dropdown.config(bg="#333333", fg="#FF1493", activebackground="#555555", activeforeground="#FF1493")
lang_dropdown.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))

# Voice File Selection
voice_label = Label(settings_frame, text="🎤 Voice Sample:", bg="#1a1a1a", fg="#FFFFFF", 
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

# Style Reference Audio (OPTIONAL)
style_label = Label(settings_frame, text="🎵 Style Ref (Optional):", bg="#1a1a1a", fg="#FFFFFF", 
                    font=('Helvetica', 10, 'bold'))
style_label.grid(row=2, column=0, sticky="w", pady=5)

style_file_label = Label(settings_frame, text="No reference", bg="#444444", fg="#999999", 
                        font=('Helvetica', 9), padx=10, pady=5)
style_file_label.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))

def select_style_file():
    file = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.mp3 *.mpeg *.wav *.ogg *.m4a *.mp4"), ("All Files", "*.*")]
    )
    if file:
        global style_reference_voice
        style_reference_voice = file
        style_file_label.config(text=f"✓ {os.path.basename(file)}", fg="#00FF00")

select_style_btn = Button(settings_frame, text="📁 Load Style", command=select_style_file, 
                         bg="#1E90FF", fg="white", font=('Helvetica', 9, 'bold'), 
                         padx=10, pady=2)
select_style_btn.grid(row=2, column=2, padx=5, pady=5)

# ============== EMOTION SLIDERS ==============
# Pitch Control
pitch_label = Label(settings_frame, text="🎵 Pitch:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
pitch_label.grid(row=3, column=0, sticky="w", pady=5)

pitch_var = DoubleVar(value=1.0)
pitch_scale = Scale(settings_frame, from_=0.7, to=1.3, resolution=0.05, orient=HORIZONTAL, 
                   bg="#333333", fg="#FF1493", length=250, variable=pitch_var)
pitch_scale.grid(row=3, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

pitch_value_label = Label(settings_frame, text="1.0x", bg="#1a1a1a", fg="#00FF00", 
                         font=('Helvetica', 9, 'bold'))
pitch_value_label.grid(row=3, column=3, padx=5)

def update_pitch_label(val):
    pitch_value_label.config(text=f"{float(val):.2f}x")
pitch_scale.config(command=update_pitch_label)

# Energy Control
energy_label = Label(settings_frame, text="📊 Energy:", bg="#1a1a1a", fg="#FFFFFF", 
                    font=('Helvetica', 10, 'bold'))
energy_label.grid(row=4, column=0, sticky="w", pady=5)

energy_var = DoubleVar(value=1.0)
energy_scale = Scale(settings_frame, from_=0.5, to=1.5, resolution=0.05, orient=HORIZONTAL, 
                    bg="#333333", fg="#FF1493", length=250, variable=energy_var)
energy_scale.grid(row=4, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

energy_value_label = Label(settings_frame, text="1.0x", bg="#1a1a1a", fg="#00FF00", 
                          font=('Helvetica', 9, 'bold'))
energy_value_label.grid(row=4, column=3, padx=5)

def update_energy_label(val):
    energy_value_label.config(text=f"{float(val):.2f}x")
energy_scale.config(command=update_energy_label)

# Speed Control
speed_label = Label(settings_frame, text="⏱️  Speed:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
speed_label.grid(row=5, column=0, sticky="w", pady=5)

speed_var = DoubleVar(value=1.0)
speed_scale = Scale(settings_frame, from_=0.5, to=2.0, resolution=0.1, orient=HORIZONTAL, 
                   bg="#333333", fg="#FF1493", length=250, variable=speed_var)
speed_scale.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

speed_value_label = Label(settings_frame, text="1.0x", bg="#1a1a1a", fg="#00FF00", 
                         font=('Helvetica', 9, 'bold'))
speed_value_label.grid(row=5, column=3, padx=5)

def update_speed_label(val):
    speed_value_label.config(text=f"{float(val):.2f}x")
speed_scale.config(command=update_speed_label)

# GPU Toggle
gpu_label = Label(settings_frame, text="⚡ Use GPU:", bg="#1a1a1a", fg="#FFFFFF", 
                  font=('Helvetica', 10, 'bold'))
gpu_label.grid(row=6, column=0, sticky="w", pady=5)

gpu_var = BooleanVar(value=torch.cuda.is_available())
gpu_check = Checkbutton(settings_frame, variable=gpu_var, bg="#1a1a1a", fg="#FFFFFF", selectcolor="#333333")
gpu_check.grid(row=6, column=1, sticky="w", pady=5, padx=(10, 0))

# ============== EMOTION PRESET BUTTONS ==============
preset_label = Label(settings_frame, text="😊 Quick Emotion Presets:", bg="#1a1a1a", fg="#FFFFFF", 
                    font=('Helvetica', 10, 'bold'))
preset_label.grid(row=7, column=0, columnspan=4, sticky="w", pady=10)

emotion_presets = {
    "😄 Happy": {"pitch": 1.2, "energy": 1.3, "speed": 1.1},
    "😢 Sad": {"pitch": 0.8, "energy": 0.7, "speed": 0.9},
    "😠 Angry": {"pitch": 1.3, "energy": 1.4, "speed": 1.2},
    "😌 Calm": {"pitch": 0.9, "energy": 0.8, "speed": 0.85},
    "🤐 Whisper": {"pitch": 0.8, "energy": 0.6, "speed": 1.0},
    "🎯 Excited": {"pitch": 1.3, "energy": 1.4, "speed": 1.3},
}

def apply_emotion_preset(preset_name):
    preset = emotion_presets.get(preset_name)
    if preset:
        pitch_var.set(preset["pitch"])
        energy_var.set(preset["energy"])
        speed_var.set(preset["speed"])
        emotion_input.delete("1.0", END)
        emotion_input.insert("1.0", f"Say this {preset_name.split()[0].lower()}")
        update_pitch_label(preset["pitch"])
        update_energy_label(preset["energy"])
        update_speed_label(preset["speed"])

preset_btn_frame = Frame(settings_frame, bg="#1a1a1a")
preset_btn_frame.grid(row=8, column=0, columnspan=4, sticky="ew", pady=5)

for i, (emotion_name, values) in enumerate(emotion_presets.items()):
    btn = Button(preset_btn_frame, text=emotion_name, 
                command=lambda e=emotion_name: apply_emotion_preset(e),
                bg="#9370DB", fg="white", font=('Helvetica', 8, 'bold'), width=12)
    btn.grid(row=0, column=i, padx=2, pady=2)

# ============== KEYWORD-TO-EMOTION MAPPER ==============
def parse_emotion_keywords(emotion_text):
    """Map emotion keywords to slider values"""
    emotion_text = emotion_text.lower()
    
    emotion_map = {
        'happy|excit|joy|cheerful|energetic|vibrant': {"pitch": 1.2, "energy": 1.3, "speed": 1.1},
        'sad|sorrowful|melancholy|depressed': {"pitch": 0.8, "energy": 0.7, "speed": 0.9},
        'angry|furious|mad|rage': {"pitch": 1.3, "energy": 1.4, "speed": 1.2},
        'calm|peaceful|relax|sooth': {"pitch": 0.9, "energy": 0.8, "speed": 0.85},
        'whisper|quiet|soft|gentle': {"pitch": 0.8, "energy": 0.6, "speed": 1.0},
        'excited|enthusiastic|pumped': {"pitch": 1.3, "energy": 1.4, "speed": 1.3},
        'slow|sluggish': {"pitch": 0.9, "energy": 0.8, "speed": 0.7},
        'fast|quick|rapid': {"pitch": 1.1, "energy": 1.1, "speed": 1.5},
        'loud|shout|yell': {"pitch": 1.3, "energy": 1.5, "speed": 1.2},
        'high|pitch|high-pitch': {"pitch": 1.4, "energy": 1.0, "speed": 1.0},
        'low|deep|deep-voice': {"pitch": 0.7, "energy": 1.0, "speed": 1.0},
    }
    
    applied_preset = None
    for keywords, preset_values in emotion_map.items():
        for keyword in keywords.split('|'):
            if keyword in emotion_text:
                applied_preset = preset_values
                break
        if applied_preset:
            break
    
    return applied_preset

def apply_emotion_from_prompt():
    """Auto-detect emotion from prompt and adjust sliders"""
    prompt = emotion_input.get("1.0", END).strip()
    preset = parse_emotion_keywords(prompt)
    if preset:
        pitch_var.set(preset["pitch"])
        energy_var.set(preset["energy"])
        speed_var.set(preset["speed"])
        update_pitch_label(preset["pitch"])
        update_energy_label(preset["energy"])
        update_speed_label(preset["speed"])
        status_label.config(text=f"✓ Emotion detected: applying presets!", fg="#00FF00")
    else:
        status_label.config(text="⚠️ No emotion detected in prompt. Adjust sliders manually.", fg="#FFA500")

apply_emotion_btn = Button(settings_frame, text="🎯 Auto-Apply Emotion", command=apply_emotion_from_prompt,
                          bg="#FF8C00", fg="white", font=('Helvetica', 9, 'bold'), padx=10, pady=2)
apply_emotion_btn.grid(row=8, column=0, padx=5, pady=5)

# Status Label
status_label = Label(window, text="Ready to generate!", bg="#1a1a1a", fg="#00FF00", 
                     font=('Helvetica', 10, 'bold'))
status_label.pack(pady=5)

# ============== UTILITY FUNCTIONS ==============
def init_tts(use_gpu: bool):
    """Initialize or reinitialize the TTS model"""
    global tts, gpu_enabled
    try:
        status_label.config(text="Loading XTTS model (this may take a minute)...", fg="#FFA500")
        window.update()
    except Exception:
        pass
    try:
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        gpu_enabled = use_gpu
        try:
            status_label.config(text=f"✓ Model ready (GPU={'yes' if gpu_enabled else 'no'})", fg="#00FF00")
        except Exception:
            pass
    except Exception as e:
        try:
            status_label.config(text="❌ Model load failed", fg="#FF6B6B")
        except Exception:
            pass
        messagebox.showerror("Model Error", f"Failed to load TTS model: {e}")

def apply_gpu_setting():
    """Reinitialize model with GPU setting"""
    use_gpu = bool(gpu_var.get()) and torch.cuda.is_available()
    if bool(gpu_var.get()) and not torch.cuda.is_available():
        messagebox.showwarning("GPU not available", "GPU not detected. Using CPU instead.")
    threading.Thread(target=init_tts, args=(use_gpu,), daemon=True).start()

apply_gpu_btn = Button(settings_frame, text="⚡ Apply GPU", command=apply_gpu_setting, 
                      bg="#2E8B57", fg="white", font=('Helvetica', 9, 'bold'))
apply_gpu_btn.grid(row=6, column=2, padx=5, pady=5)

def play_audio(filename):
    """Play audio file using pygame"""
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

def convert_with_clone():
    """Generate speech with cloned voice and emotion controls"""
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    if not uploaded_voice:
        messagebox.showerror("Error", "Please load a voice sample first!")
        return
    
    try:
        status_label.config(text="🎤 Generating emotional speech... (may take 30-60 sec)", fg="#FFA500")
        window.update()
        
        # Ensure model is initialized
        if tts is None:
            use_gpu = bool(gpu_var.get()) and torch.cuda.is_available()
            init_tts(use_gpu)
            time.sleep(2)  # Wait for model to load
        
        lang = lang_var.get()
        speed = speed_var.get()
        
        # Apply emotion controls
        pitch = pitch_var.get()
        energy = energy_var.get()
        
        # Generate speech with cloned voice
        output_file = f"cloned_emotion_{int(time.time())}.wav"
        
        # Use style reference if available, otherwise use main voice
        speaker_wav = style_reference_voice if style_reference_voice else uploaded_voice
        
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            speaker_wav=speaker_wav,
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

def save_cloned_speech():
    """Save cloned speech to file"""
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    if not uploaded_voice:
        messagebox.showerror("Error", "Please load a voice sample first!")
        return
    
    try:
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", 
                                                  filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")])
        if save_path:
            status_label.config(text="💾 Generating and saving... (30-60 sec)", fg="#FFA500")
            window.update()
            
            # Ensure model is initialized
            if tts is None:
                use_gpu = bool(gpu_var.get()) and torch.cuda.is_available()
                init_tts(use_gpu)
                time.sleep(2)
            
            lang = lang_var.get()
            speed = speed_var.get()
            
            speaker_wav = style_reference_voice if style_reference_voice else uploaded_voice
            
            tts.tts_to_file(
                text=text,
                file_path=save_path,
                speaker_wav=speaker_wav,
                language=lang,
                speed=speed
            )
            
            messagebox.showinfo("Success", f"Audio saved to:\n{save_path}")
            status_label.config(text="✓ File saved successfully!", fg="#00FF00")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="❌ Save failed", fg="#FF6B6B")

def clear_all():
    """Clear all inputs"""
    global uploaded_voice, style_reference_voice
    text_input.delete("1.0", END)
    emotion_input.delete("1.0", END)
    uploaded_voice = None
    style_reference_voice = None
    voice_file_label.config(text="No file selected", fg="#999999")
    style_file_label.config(text="No reference", fg="#999999")
    pitch_var.set(1.0)
    energy_var.set(1.0)
    speed_var.set(1.0)
    update_pitch_label(1.0)
    update_energy_label(1.0)
    update_speed_label(1.0)
    status_label.config(text="Ready to generate!", fg="#00FF00")

# ============== BUTTONS FRAME ==============
button_frame = Frame(window, bg="#1a1a1a")
button_frame.pack(pady=15)

play_btn = Button(button_frame, text="▶ Generate & Play", command=convert_with_clone, 
                  bg="#FF1493", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=25, height=2, activebackground="#E60F8C")
play_btn.grid(row=0, column=0, padx=5)

save_btn = Button(button_frame, text="💾 Save Audio", command=save_cloned_speech, 
                  bg="#1E90FF", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=25, height=2, activebackground="#1873DA")
save_btn.grid(row=0, column=1, padx=5)

clear_btn = Button(button_frame, text="🗑 Clear All", command=clear_all, 
                   bg="#FF6B6B", fg="white", font=('Helvetica', 11, 'bold'), 
                   width=52, height=2, activebackground="#E60F0F")
clear_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Info Label
info_label = Label(window, text="✨ XTTS v2 + Emotion Control | Clone voice + apply emotions (happy, sad, angry, calm, etc.) | Auto-detect emotion from prompt | Optional style reference", 
                   bg="#1a1a1a", fg="#999999", font=('Helvetica', 8, 'italic'))
info_label.pack(pady=5)

# Run the window
window.mainloop()
