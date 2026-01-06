"""
Jarvis TTS Module - Simple gTTS Implementation
Generates speech from text using Google Text-to-Speech
"""

import os
import sys
import time
from gtts import gTTS

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
except ImportError:
    class Config:
        pass


class TextToSpeech:
    """Simple TTS using gTTS"""
    
    def __init__(self, voice_sample_path=None, use_gpu=None):
        """Initialize TTS"""
        self.config = Config()
        self.voice_sample_path = voice_sample_path
        print(f"[TTS] ✅ Ready (gTTS)")
    
    def wait_for_model(self, timeout=300):
        """No waiting needed"""
        pass
    
    def speak(self, text, speaker_wav=None, language='en', speed=1.0, 
              output_file=None, auto_play=True):
        """
        Generate speech using gTTS
        
        Args:
            text: Text to speak
            speaker_wav: Ignored (gTTS doesn't need voice file)
            language: Language code
            speed: Ignored (gTTS doesn't support speed control)
            output_file: Save audio to file
            auto_play: Play after generation
            
        Returns:
            Path to generated audio file
        """
        try:
            if not output_file:
                output_file = f"/tmp/jarvis_speech_{int(time.time() * 1000)}.mp3"
            
            text_preview = text[:50] + "..." if len(text) > 50 else text
            print(f"[TTS] Generating: '{text_preview}'")
            
            # Generate speech with gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_file)
            
            print(f"[TTS] ✅ Generated: {output_file}")
            
            if auto_play:
                self.play_audio(output_file)
            
            return output_file
            
        except Exception as e:
            print(f"[ERROR] TTS error: {e}")
            return None
    
    @staticmethod
    def play_audio(file_path, blocking=True):
        """Play audio file"""
        if not os.path.exists(file_path):
            print(f"[ERROR] Audio file not found: {file_path}")
            return
        
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            if blocking:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
            print(f"[TTS] ✅ Playback finished")
            
        except Exception as e:
            print(f"[ERROR] Playback error: {e}")
    
    def set_voice_sample(self, voice_path):
        """Set voice file (not used with gTTS)"""
        if os.path.exists(voice_path):
            self.voice_sample_path = voice_path
            print(f"[TTS] Voice set: {os.path.basename(voice_path)}")
            return True
        else:
            print(f"[ERROR] Voice file not found: {voice_path}")
            return False
    
    def is_ready(self):
        """Always ready"""
        return True

