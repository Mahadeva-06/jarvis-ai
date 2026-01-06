"""
Jarvis - AI Voice Assistant
Main entry point with GUI implementation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
from stt import SpeechToText
from actions import Actions
from tts import TextToSpeech
from config import Config


class JarvisGUI:
    """Jarvis Voice Assistant GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Jarvis - AI Voice Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2e")
        
        # Initialize modules
        self.config = Config()
        self.stt = SpeechToText()
        self.actions = Actions()
        self.tts = TextToSpeech(
            voice_sample_path=self.config.DEFAULT_VOICE,
            use_gpu=self.config.TTS_USE_GPU
        )
        
        # State variables
        self.listening = False
        self.running = True
        
        # Create GUI
        self.create_widgets()
        self.setup_styles()
        
        # Introduce Jarvis with voice
        self.root.after(500, self.introduce_jarvis)
        
    def setup_styles(self):
        """Setup custom styles for tkinter"""
        self.root.option_add('*Font', ('Segoe UI', 10))
        
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Header frame
        header_frame = tk.Frame(self.root, bg="#2d2d44", height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title and Voice Menu Container
        title_menu_frame = tk.Frame(header_frame, bg="#2d2d44")
        title_menu_frame.pack(fill=tk.X, padx=20)
        
        # Title
        title_label = tk.Label(
            title_menu_frame,
            text="🤖 JARVIS",
            font=("Segoe UI", 28, "bold"),
            bg="#2d2d44",
            fg="#00d4ff"
        )
        title_label.pack(side=tk.LEFT, pady=10)
        
        # Voice Menu Button
        voice_menu_btn = tk.Menubutton(
            title_menu_frame,
            text="🎙️ Voices ▼",
            font=("Segoe UI", 10, "bold"),
            bg="#00d4ff",
            fg="#000000",
            activebackground="#00a8cc",
            relief=tk.RAISED,
            bd=2,
            padx=15,
            pady=5
        )
        voice_menu_btn.pack(side=tk.RIGHT, padx=(10, 0), pady=10)
        
        # Create voice menu
        voice_menu = tk.Menu(voice_menu_btn, tearoff=0, bg="#333333", fg="#ffffff")
        voice_menu_btn.config(menu=voice_menu)
        
        # Load available voices
        self.available_voices = self._load_available_voices()
        self.current_voice = tk.StringVar(value="jarvis_voice")
        
        for voice_file in self.available_voices:
            voice_name = voice_file.replace('_', ' ').replace('.wav', '').title()
            voice_menu.add_radiobutton(
                label=voice_name,
                variable=self.current_voice,
                value=voice_file,
                command=lambda v=voice_file: self.change_voice(v)
            )
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI Voice Assistant for Laptop Control",
            font=("Segoe UI", 10),
            bg="#2d2d44",
            fg="#a0a0a0"
        )
        subtitle_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg="#1e1e2e")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Status frame
        status_frame = tk.Frame(content_frame, bg="#252535", relief=tk.RIDGE, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        status_label = tk.Label(
            status_frame,
            text="Status:",
            font=("Segoe UI", 10, "bold"),
            bg="#252535",
            fg="#00d4ff"
        )
        status_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_display = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg="#252535",
            fg="#00ff00"
        )
        self.status_display.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Output text area
        output_label = tk.Label(
            content_frame,
            text="Command History:",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e2e",
            fg="#00d4ff"
        )
        output_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            content_frame,
            height=12,
            width=80,
            bg="#252535",
            fg="#00ff00",
            font=("Consolas", 9),
            insertbackground="#00d4ff",
            relief=tk.SUNKEN,
            bd=1
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Input frame
        input_frame = tk.Frame(content_frame, bg="#1e1e2e")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        input_label = tk.Label(
            input_frame,
            text="Command:",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e2e",
            fg="#00d4ff"
        )
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.input_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 10),
            bg="#252535",
            fg="#00ff00",
            insertbackground="#00d4ff",
            relief=tk.SUNKEN,
            bd=1
        )
        self.input_entry.pack(fill=tk.X)
        self.input_entry.bind("<Return>", lambda e: self.execute_text_command())
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg="#1e1e2e")
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Start button
        start_btn = tk.Button(
            button_frame,
            text="▶ START",
            command=self.start_jarvis,
            font=("Segoe UI", 12, "bold"),
            bg="#00ff00",
            fg="#000000",
            activebackground="#00cc00",
            relief=tk.RAISED,
            bd=3,
            padx=25,
            pady=12,
            width=18
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Listen button
        self.listen_btn = tk.Button(
            button_frame,
            text="🎤 Listen",
            command=self.start_listening,
            font=("Segoe UI", 11, "bold"),
            bg="#00d4ff",
            fg="#000000",
            activebackground="#00a8cc",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10,
            width=15
        )
        self.listen_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Execute button
        execute_btn = tk.Button(
            button_frame,
            text="✓ Execute",
            command=self.execute_text_command,
            font=("Segoe UI", 11, "bold"),
            bg="#00d4ff",
            fg="#000000",
            activebackground="#00a8cc",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10,
            width=15
        )
        execute_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️  Clear",
            command=self.clear_output,
            font=("Segoe UI", 11, "bold"),
            bg="#666666",
            fg="#ffffff",
            activebackground="#555555",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10,
            width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Exit button
        exit_btn = tk.Button(
            button_frame,
            text="⏻️  Exit",
            command=self.exit_app,
            font=("Segoe UI", 11, "bold"),
            bg="#ff4444",
            fg="#ffffff",
            activebackground="#cc0000",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10,
            width=15
        )
        exit_btn.pack(side=tk.LEFT)
        
        # Footer frame
        footer_frame = tk.Frame(self.root, bg="#2d2d44", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text=f"Jarvis v{self.config.VERSION} | Ready to assist",
            font=("Segoe UI", 9),
            bg="#2d2d44",
            fg="#666666"
        )
        footer_label.pack(pady=12)
    
    def _load_available_voices(self):
        """Load all available voice files from voices directory"""
        import os
        voices_dir = self.config.VOICES_DIR
        
        if not os.path.exists(voices_dir):
            return []
        
        voice_files = []
        for file in os.listdir(voices_dir):
            if file.endswith('.wav') or file.endswith('.mp3'):
                voice_files.append(file)
        
        return sorted(voice_files) if voice_files else []
    
    def change_voice(self, voice_file):
        """Change the TTS voice"""
        voice_path = os.path.join(self.config.VOICES_DIR, voice_file)
        
        if os.path.exists(voice_path):
            self.tts.set_voice_sample(voice_path)
            voice_name = voice_file.replace('_', ' ').replace('.wav', '').title()
            self.log_output(f"[VOICE] Changed to: {voice_name}")
            self.status_var.set(f"Voice: {voice_name}")
            messagebox.showinfo("Voice Changed", f"Switched to {voice_name}")
        else:
            messagebox.showerror("Error", f"Voice file not found: {voice_path}")
        
    def log_output(self, message):
        """Add message to output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()
    
    def start_jarvis(self):
        """Start Jarvis and introduce itself"""
        self.log_output("[JARVIS] Starting up...")
        self.status_var.set("Starting Jarvis...")
        self.introduce_jarvis()
    
    def introduce_jarvis(self):
        """Jarvis introduces itself using voice cloning"""
        introduction = "Hello! I am Jarvis, your personal AI assistant. I am ready to help you with voice commands and laptop control. Click the listen button to get started."
        
        self.log_output("[JARVIS] " + introduction)
        self.status_var.set("Introducing myself...")
        
        # Speak introduction in background thread
        thread = threading.Thread(
            target=self._speak_introduction,
            args=(introduction,),
            daemon=True
        )
        thread.start()
    
    def _speak_introduction(self, text):
        """Thread function to speak introduction"""
        try:
            # Wait for TTS model to be ready
            if not self.tts.is_ready():
                self.log_output("[TTS] Waiting for voice engine to initialize...")
                self.tts.wait_for_model(timeout=120)
            
            if self.tts.is_ready():
                self.status_var.set("Speaking introduction...")
                self.tts.speak(
                    text=text,
                    language='en',
                    speed=1.0,
                    auto_play=True
                )
                self.status_var.set("Ready to listen!")
            else:
                self.log_output("[WARNING] Voice engine not ready. Running in text mode.")
                self.status_var.set("Ready (text mode)")
                
        except Exception as e:
            self.log_output(f"[ERROR] Voice introduction failed: {str(e)}")
            self.status_var.set("Ready (voice unavailable)")
        
    def start_listening(self):
        """Start voice listening in a separate thread"""
        if not self.listening:
            self.listening = True
            self.listen_btn.config(state=tk.DISABLED, text="🎤 Listening...", bg="#ff9800")
            self.status_var.set("Listening...")
            self.log_output("[INFO] Listening for voice command...")
            
            # Run listening in a thread to avoid blocking GUI
            thread = threading.Thread(target=self._listen_thread)
            thread.daemon = True
            thread.start()
    
    def _listen_thread(self):
        """Thread function for listening"""
        try:
            text = self.stt.listen()
            
            if text:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text)
                self.log_output(f"[VOICE] You said: {text}")
                self.status_var.set(f"Recognized: {text[:30]}...")
                
                # Auto-execute if speech was recognized
                self.root.after(500, self.execute_text_command)
            else:
                self.log_output("[ERROR] Could not recognize speech")
                self.status_var.set("Speech not recognized")
                
        except Exception as e:
            self.log_output(f"[ERROR] {str(e)}")
            self.status_var.set("Error occurred")
        finally:
            self.listening = False
            self.root.after(0, self._update_listen_button)
    
    def _update_listen_button(self):
        """Update listen button state"""
        self.listen_btn.config(state=tk.NORMAL, text="🎤 Listen", bg="#00d4ff")
    
    def execute_text_command(self):
        """Execute command from text input"""
        command = self.input_entry.get().strip()
        
        if command:
            self.log_output(f"[COMMAND] Executing: {command}")
            self.status_var.set(f"Executing: {command[:30]}...")
            
            try:
                self.actions.process_command(command)
                self.log_output(f"[SUCCESS] Command executed")
                self.status_var.set("Command executed")
            except Exception as e:
                self.log_output(f"[ERROR] {str(e)}")
                self.status_var.set("Error occurred")
            
            self.input_entry.delete(0, tk.END)
    
    def clear_output(self):
        """Clear output text area"""
        self.output_text.delete(1.0, tk.END)
        self.log_output("[INFO] Output cleared")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit Jarvis?"):
            self.running = False
            self.root.quit()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = JarvisGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nJarvis shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
