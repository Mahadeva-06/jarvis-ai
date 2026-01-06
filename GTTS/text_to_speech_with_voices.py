#!/usr/bin/env python3
# Text to Speech Converter with Multiple Voices (Male/Female)

import pyttsx3
from gtts import gTTS
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import pygame
import os
import time
import threading

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Create Window
window = Tk()
window.geometry('700x550')
window.resizable(0, 0)
window.title("Text to Speech Converter - Multi Voice Edition")
window.config(bg='#2c3e50')

# Title Label
title = Label(window, text="Text to Speech Converter", bg="#2c3e50", fg="#FFFF00", 
              font=('Helvetica', 25, 'bold'))
title.pack(pady=15)

# Label for instructions
instruction = Label(window, text="Enter text below and convert to audio:", 
                    bg="#2c3e50", fg="white", font=('Helvetica', 12))
instruction.pack()

# Text Input Area
text_input = Text(window, height=7, width=50, bg="white", fg="black", 
                  font=('Helvetica', 11))
text_input.pack(pady=10, padx=20)

# Options Frame
options_frame = Frame(window, bg="#2c3e50")
options_frame.pack(pady=10)

# Voice Gender Selection
gender_label = Label(options_frame, text="Voice Gender:", bg="#2c3e50", fg="white", 
                     font=('Helvetica', 10, 'bold'))
gender_label.grid(row=0, column=0, padx=5)

gender_var = StringVar(value='male')
male_radio = Radiobutton(options_frame, text="Male", variable=gender_var, value='male', 
                         bg="#2c3e50", fg="white", selectcolor="#27ae60", 
                         activebackground="#2c3e50", activeforeground="white")
male_radio.grid(row=0, column=1, padx=5)

female_radio = Radiobutton(options_frame, text="Female", variable=gender_var, value='female', 
                           bg="#2c3e50", fg="white", selectcolor="#e74c3c", 
                           activebackground="#2c3e50", activeforeground="white")
female_radio.grid(row=0, column=2, padx=5)

# Speech Rate Adjustment
rate_label = Label(options_frame, text="Speed:", bg="#2c3e50", fg="white", 
                   font=('Helvetica', 10, 'bold'))
rate_label.grid(row=1, column=0, padx=5, pady=10)

rate_var = IntVar(value=150)
rate_scale = Scale(options_frame, from_=50, to=300, orient=HORIZONTAL, 
                   bg="#34495e", fg="white", length=200, variable=rate_var)
rate_scale.grid(row=1, column=1, columnspan=2, padx=5, pady=10)

# Volume Adjustment
volume_label = Label(options_frame, text="Volume:", bg="#2c3e50", fg="white", 
                     font=('Helvetica', 10, 'bold'))
volume_label.grid(row=2, column=0, padx=5, pady=10)

volume_var = IntVar(value=100)
volume_scale = Scale(options_frame, from_=0, to=100, orient=HORIZONTAL, 
                     bg="#34495e", fg="white", length=200, variable=volume_var)
volume_scale.grid(row=2, column=1, columnspan=2, padx=5, pady=10)

# Status Label
status_label = Label(window, text="", bg="#2c3e50", fg="#00FF00", 
                     font=('Helvetica', 10, 'bold'))
status_label.pack(pady=5)

# Function to get available voices
def get_voices():
    voices = engine.getProperty('voices')
    male_voices = [v for v in voices if 'male' in v.name.lower()]
    female_voices = [v for v in voices if 'female' in v.name.lower()]
    
    if not male_voices and voices:
        male_voices = [voices[0]]
    if not female_voices and len(voices) > 1:
        female_voices = [voices[1]]
    
    return male_voices, female_voices

# Function to play audio using pygame
def play_audio_pygame(filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        # Note: pygame volume control doesn't work for all formats, use engine volume instead
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        messagebox.showerror("Playback Error", f"Error playing audio: {str(e)}\n\nTip: Make sure the file is a valid WAV or MP3 file.")

# Function to convert using pyttsx3 (local voices)
def convert_with_pyttsx3():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    try:
        status_label.config(text="Converting (pyttsx3)... Please wait...")
        window.update()
        
        # Set voice
        male_voices, female_voices = get_voices()
        gender = gender_var.get()
        
        if gender == 'male' and male_voices:
            engine.setProperty('voice', male_voices[0].id)
        elif gender == 'female' and female_voices:
            engine.setProperty('voice', female_voices[0].id)
        
        # Set rate and volume
        engine.setProperty('rate', rate_var.get())
        engine.setProperty('volume', volume_var.get() / 100.0)
        
        # Save and play (pyttsx3 saves as WAV on Linux)
        filename = "output_pyttsx3.wav"
        engine.save_to_file(text, filename)
        engine.runAndWait()
        
        status_label.config(text="✓ Audio ready! Playing...")
        window.update()
        
        time.sleep(1)
        play_audio_pygame(filename)
        status_label.config(text="✓ Playback completed!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="Error occurred")

# Function to convert using gTTS (requires internet but may sound better)
def convert_with_gtts():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    try:
        status_label.config(text="Converting (gTTS - online)... Please wait...")
        window.update()
        
        tts = gTTS(text=text, lang='en', slow=False)
        filename = "output_gtts.mp3"
        tts.save(filename)
        
        status_label.config(text="✓ Audio ready! Playing...")
        window.update()
        
        play_audio_pygame(filename)
        status_label.config(text="✓ Playback completed!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="Error occurred")

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
            male_voices, female_voices = get_voices()
            gender = gender_var.get()
            
            if gender == 'male' and male_voices:
                engine.setProperty('voice', male_voices[0].id)
            elif gender == 'female' and female_voices:
                engine.setProperty('voice', female_voices[0].id)
            
            engine.setProperty('rate', rate_var.get())
            engine.setProperty('volume', volume_var.get() / 100.0)
            
            engine.save_to_file(text, save_path)
            engine.runAndWait()
            
            messagebox.showinfo("Success", f"Audio saved to:\n{save_path}")
            status_label.config(text="✓ Audio saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")

# Function to clear text
def clear_text():
    text_input.delete("1.0", END)
    status_label.config(text="")

# Buttons Frame
button_frame = Frame(window, bg="#2c3e50")
button_frame.pack(pady=15)

# Convert with pyttsx3 (Local - Male/Female support)
convert_local_btn = Button(button_frame, text="Play (Local Voice)", 
                          command=convert_with_pyttsx3, 
                          bg="#27ae60", fg="white", font=('Helvetica', 10, 'bold'), 
                          width=18, height=2)
convert_local_btn.grid(row=0, column=0, padx=5)

# Convert with gTTS (Online - Natural sound)
convert_online_btn = Button(button_frame, text="Play (Online Voice)", 
                           command=convert_with_gtts, 
                           bg="#3498db", fg="white", font=('Helvetica', 10, 'bold'), 
                           width=18, height=2)
convert_online_btn.grid(row=0, column=1, padx=5)

# Save Button
save_btn = Button(button_frame, text="Save Audio", command=save_audio, 
                  bg="#e67e22", fg="white", font=('Helvetica', 10, 'bold'), 
                  width=18, height=2)
save_btn.grid(row=1, column=0, padx=5, pady=5)

# Clear Button
clear_btn = Button(button_frame, text="Clear", command=clear_text, 
                   bg="#95a5a6", fg="white", font=('Helvetica', 10, 'bold'), 
                   width=18, height=2)
clear_btn.grid(row=1, column=1, padx=5, pady=5)

# Info Label
info_label = Label(window, text="Local Voice = Male/Female WAV files | Online Voice = MP3 format (needs internet)", 
                   bg="#2c3e50", fg="#ecf0f1", font=('Helvetica', 8, 'italic'))
info_label.pack(pady=5)

# Run the window
window.mainloop()
