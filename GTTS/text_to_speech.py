#!/usr/bin/env python3
# Text to Speech Converter using gTTS

from gtts import gTTS
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import pygame
import os
import time

# Create Window
window = Tk()
window.geometry('600x400')
window.resizable(0, 0)
window.title("Text to Speech Converter")
window.config(bg='#2c3e50')

# Title Label
title = Label(window, text="Text to Speech Converter", bg="#2c3e50", fg="#FFFF00", 
              font=('Helvetica', 25, 'bold'))
title.pack(pady=20)

# Label for instructions
instruction = Label(window, text="Enter text below and convert to audio:", 
                    bg="#2c3e50", fg="white", font=('Helvetica', 12))
instruction.pack()

# Text Input Area
text_input = Text(window, height=8, width=50, bg="white", fg="black", 
                  font=('Helvetica', 11))
text_input.pack(pady=10, padx=20)

# Label for language selection
lang_label = Label(window, text="Select Language:", bg="#2c3e50", fg="white", 
                   font=('Helvetica', 10))
lang_label.pack()

# Language dropdown
lang_var = StringVar(value='en')
lang_dropdown = OptionMenu(window, lang_var, 'en', 'es', 'fr', 'de', 'hi', 'ja', 'ar')
lang_dropdown.config(bg="white", fg="black")
lang_dropdown.pack()

# Status Label
status_label = Label(window, text="", bg="#2c3e50", fg="#00FF00", 
                     font=('Helvetica', 10))
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
    except Exception as e:
        messagebox.showerror("Playback Error", f"Error playing audio: {str(e)}")

# Function to convert text to speech
def convert_to_speech():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    try:
        status_label.config(text="Converting... Please wait...")
        window.update()
        
        lang = lang_var.get()
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to file
        filename = "output.mp3"
        tts.save(filename)
        
        status_label.config(text="✓ Audio saved as 'output.mp3'")
        
        # Play the audio using pygame
        messagebox.showinfo("Success", "Audio saved! Playing now...")
        play_audio_pygame("output.mp3")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")
        status_label.config(text="Error occurred")

# Function to play existing file
def play_audio():
    if os.path.exists("output.mp3"):
        play_audio_pygame("output.mp3")
    else:
        messagebox.showwarning("Warning", "No audio file found. Convert first!")

# Function to save audio with custom name
def save_audio():
    text = text_input.get("1.0", END).strip()
    
    if not text:
        messagebox.showerror("Error", "Please enter some text!")
        return
    
    try:
        save_path = filedialog.asksaveasfilename(defaultextension=".mp3", 
                                                  filetypes=[("MP3 files", "*.mp3")])
        if save_path:
            lang = lang_var.get()
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(save_path)
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

# Convert Button
convert_btn = Button(button_frame, text="Convert & Play", command=convert_to_speech, 
                     bg="#27ae60", fg="white", font=('Helvetica', 11, 'bold'), 
                     width=15, height=2)
convert_btn.grid(row=0, column=0, padx=5)

# Save Button
save_btn = Button(button_frame, text="Save Custom", command=save_audio, 
                  bg="#3498db", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=15, height=2)
save_btn.grid(row=0, column=1, padx=5)

# Play Button
play_btn = Button(button_frame, text="Play Last", command=play_audio, 
                  bg="#e74c3c", fg="white", font=('Helvetica', 11, 'bold'), 
                  width=15, height=2)
play_btn.grid(row=0, column=2, padx=5)

# Clear Button
clear_btn = Button(button_frame, text="Clear", command=clear_text, 
                   bg="#95a5a6", fg="white", font=('Helvetica', 11, 'bold'), 
                   width=15, height=2)
clear_btn.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky="ew")

# Run the window
window.mainloop()
