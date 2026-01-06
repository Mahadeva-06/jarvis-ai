#!/usr/bin/env python3
# Enhanced Text to Speech with gTTS - Multiple Languages & Voices

from gtts import gTTS
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import pygame
import os
import time
import threading

# Create Window
window = Tk()
window.geometry('800x650')
window.resizable(0, 0)
window.title("Text to Speech Converter - Enhanced gTTS")
window.config(bg='#1a1a1a')

# Title Label
title = Label(window, text="Advanced Text to Speech", bg="#1a1a1a", fg="#00FF00", 
              font=('Helvetica', 28, 'bold'))
title.pack(pady=15)

# Language and Voice Mapping (Different languages = different voices/tones)
LANGUAGE_VOICES = {
    'English (Natural)': 'en',
    'English (British)': 'en-gb',
    'English (US)': 'en-us',
    'Spanish (Spain)': 'es',
    'Spanish (Mexico)': 'es-mx',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese (Brazil)': 'pt-br',
    'Portuguese (Portugal)': 'pt-pt',
    'Chinese (Mandarin)': 'zh-cn',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Hindi': 'hi',
    'Russian': 'ru',
    'Arabic': 'ar',
    'Turkish': 'tr',
    'Polish': 'pl',
    'Thai': 'th',
    'Vietnamese': 'vi',
}

# Text Input Area
instruction = Label(window, text="Enter text below and convert to audio:", 
                    bg="#1a1a1a", fg="#FFFFFF", font=('Helvetica', 11))
instruction.pack()

text_input = Text(window, height=7, width=60, bg="#333333", fg="#FFFFFF", 
                  font=('Helvetica', 11), insertbackground='#00FF00')
text_input.pack(pady=10, padx=20)

# Options Frame
options_frame = LabelFrame(window, text="Voice Settings", bg="#1a1a1a", fg="#00FF00", 
                           font=('Helvetica', 10, 'bold'), padx=15, pady=10)
options_frame.pack(pady=10, padx=20, fill="x")

# Language Selection
lang_label = Label(options_frame, text="Language/Voice:", bg="#1a1a1a", fg="#FFFFFF", 
                   font=('Helvetica', 10, 'bold'))
lang_label.grid(row=0, column=0, sticky="w", pady=5)

lang_var = StringVar(value='English (Natural)')
lang_dropdown = OptionMenu(options_frame, lang_var, *LANGUAGE_VOICES.keys())
lang_dropdown.config(bg="#333333", fg="#00FF00", activebackground="#555555", activeforeground="#00FF00")
lang_dropdown.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

# Speed Selection
speed_label = Label(options_frame, text="Speed:", bg="#1a1a1a", fg="#FFFFFF", 
                    font=('Helvetica', 10, 'bold'))
speed_label.grid(row=1, column=0, sticky="w", pady=5)

speed_var = StringVar(value='normal')
speed_frame = Frame(options_frame, bg="#1a1a1a")
speed_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5, padx=(10, 0))

Radiobutton(speed_frame, text="Slow", variable=speed_var, value='slow', 
            bg="#1a1a1a", fg="#FFFFFF", selectcolor="#00FF00", 
            activebackground="#1a1a1a", activeforeground="#00FF00").pack(side=LEFT, padx=5)
Radiobutton(speed_frame, text="Normal", variable=speed_var, value='normal', 
            bg="#1a1a1a", fg="#FFFFFF", selectcolor="#00FF00", 
            activebackground="#1a1a1a", activeforeground="#00FF00").pack(side=LEFT, padx=5)
Radiobutton(speed_frame, text="Fast", variable=speed_var, value='fast', 
            bg="#1a1a1a", fg="#FFFFFF", selectcolor="#00FF00", 
            activebackground="#1a1a1a", activeforeground="#00FF00").pack(side=LEFT, padx=5)

# Status Label
status_label = Label(window, text="Ready", bg="#1a1a1a", fg="#00FF00", 
                     font=('Helvetica', 10, 'bold'))
status_label.pack(pady=5)

# Function to play audio using pygame
def play_audio_pygame(filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        status_label.config(text="✓ Playback completed!")
    except Exception as e:
        messagebox.showerror("Playback Error", f"Error playing audio: {str(e)}")
        status_label.config(text="❌ Playback error")

# Function to convert text to speech
def convert_and_play():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    try:
        status_label.config(text="Converting... Please wait...")
        window.update()
        
        # Get selected language and speed
        lang_name = lang_var.get()
        lang_code = LANGUAGE_VOICES[lang_name]
        speed = speed_var.get() == 'slow'  # True for slow, False for normal/fast
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang_code, slow=speed)
        
        # Save to file
        filename = f"output_{lang_code.replace('-', '_')}.mp3"
        tts.save(filename)
        
        status_label.config(text="✓ Audio ready! Playing...")
        window.update()
        
        time.sleep(0.5)
        play_audio_pygame(filename)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}\n\nMake sure you have internet connection!")
        status_label.config(text="❌ Error occurred")

# Function to save audio
def save_audio():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    try:
        save_path = filedialog.asksaveasfilename(defaultextension=".mp3", 
                                                  filetypes=[("MP3 files", "*.mp3")])
        if save_path:
            status_label.config(text="Saving... Please wait...")
            window.update()
            
            lang_name = lang_var.get()
            lang_code = LANGUAGE_VOICES[lang_name]
            speed = speed_var.get() == 'slow'
            
            tts = gTTS(text=text, lang=lang_code, slow=speed)
            tts.save(save_path)
            
            messagebox.showinfo("Success", f"Audio saved to:\n{save_path}")
            status_label.config(text="✓ File saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="❌ Save failed")

# Function to clear text
def clear_text():
    text_input.delete("1.0", END)
    status_label.config(text="Ready")

# Function to show available voices
def show_info():
    info_text = "Available Languages/Voices:\n\n"
    for i, lang in enumerate(LANGUAGE_VOICES.keys(), 1):
        info_text += f"{i}. {lang}\n"
    
    info_window = Toplevel(window)
    info_window.title("Available Voices")
    info_window.geometry("400x500")
    info_window.config(bg="#1a1a1a")
    
    text_widget = Text(info_window, height=25, width=45, bg="#333333", fg="#00FF00",
                       font=('Courier', 9))
    text_widget.pack(padx=10, pady=10, fill="both", expand=True)
    text_widget.insert("1.0", info_text)
    text_widget.config(state=DISABLED)
    
    scrollbar = Scrollbar(text_widget, command=text_widget.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    text_widget.config(yscrollcommand=scrollbar.set)

# Buttons Frame
button_frame = Frame(window, bg="#1a1a1a")
button_frame.pack(pady=15)

# Convert Button
convert_btn = Button(button_frame, text="▶ Play & Hear", command=convert_and_play, 
                     bg="#27ae60", fg="white", font=('Helvetica', 11, 'bold'), 
                     width=20, height=2, activebackground="#229954")
convert_btn.grid(row=0, column=0, padx=5)

# Save Button
save_btn = Button(button_frame, text="💾 Save Audio", command=save_audio, 
                  bg="#2980b9", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=20, height=2, activebackground="#1f618d")
save_btn.grid(row=0, column=1, padx=5)

# Info Button
info_btn = Button(button_frame, text="ℹ Voices Info", command=show_info, 
                  bg="#8e44ad", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=20, height=2, activebackground="#6c3483")
info_btn.grid(row=1, column=0, padx=5, pady=5)

# Clear Button
clear_btn = Button(button_frame, text="🗑 Clear", command=clear_text, 
                   bg="#e74c3c", fg="white", font=('Helvetica', 11, 'bold'), 
                   width=20, height=2, activebackground="#cb4335")
clear_btn.grid(row=1, column=1, padx=5, pady=5)

# Info Label
info_label = Label(window, text="Powered by Google Text-to-Speech (gTTS) | Internet Required | 20+ Languages Available", 
                   bg="#1a1a1a", fg="#999999", font=('Helvetica', 8, 'italic'))
info_label.pack(pady=5)

# Run the window
window.mainloop()
