"""
Jarvis TTS Module - Consumer of Pre-Cloned Voices
Uses Piper (lightweight TTS) with pre-cloned voice files
XTTS is ONLY for voice cloning (separate script)
"""

import os
import sys
import time
import subprocess

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
except ImportError:
    # Fallback if config not available
    class Config:
        pass


class TextToSpeech:
    """
    Jarvis TTS - Uses pre-cloned voices with Piper.
    
    Architecture:
    - Stage 1: XTTS clones voice ONCE → saves brade_clone.wav
    - Stage 2: Jarvis uses Piper with that voice file
    
    No XTTS at runtime. Clean separation. Fast execution.
    """
    
    def __init__(self, voice_sample_path=None, use_gpu=None):
        """
        Initialize TTS with pre-cloned voice file
        
        Args:
            voice_sample_path: Path to pre-cloned voice WAV (brade_clone.wav)
            use_gpu: Ignored (Piper is lightweight)
        """
        self.config = Config()
        self.voice_sample_path = voice_sample_path
        
        # Check if voice file exists
        if self.voice_sample_path and os.path.exists(self.voice_sample_path):
            print(f"[TTS] ✅ Ready with voice: {os.path.basename(self.voice_sample_path)}")
        else:
            print(f"[TTS] ⚠️ Voice file not found, using default")
    
    def wait_for_model(self, timeout=300):
        """No waiting needed - Piper is instant!"""
        pass
    
    def speak(self, text, speaker_wav=None, language='en', speed=1.0, 
              output_file=None, auto_play=True):
        """
        Generate speech using pre-cloned voice with Piper.
        
        Args:
            text: ANY dynamic text
            speaker_wav: Voice file (brade_clone.wav)
            language: Language code (en, es, fr, etc.)
            speed: Speech speed
            output_file: Save audio to file
            auto_play: Play after generation
            
        Returns:
            Path to generated audio file
        """
        try:
            # Use provided voice or default
            voice_wav = speaker_wav or self.voice_sample_path
            
            if not voice_wav or not os.path.exists(voice_wav):
                print(f"[ERROR] Voice file not found: {voice_wav}")
                return None
            
            if not output_file:
                output_file = f"jarvis_speech_{int(time.time())}.wav"
            
            text_preview = text[:50] + "..." if len(text) > 50 else text
            print(f"[TTS] Generating: '{text_preview}'")
            print(f"[TTS] Using voice: {os.path.basename(voice_wav)}")
            
            # Generate speech using Piper with voice conditioning
            # Piper: echo "text" | piper --voice voice.wav -o output.wav
            try:
                process = subprocess.Popen(
                    ['piper', '--speaker', voice_wav, '--output-file', output_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=text)
                
                if process.returncode != 0:
                    print(f"[WARNING] Piper not available, using fallback")
                    return self._fallback_speak(text, output_file, auto_play)
                
            except FileNotFoundError:
                print(f"[WARNING] Piper not installed, using fallback TTS")
                return self._fallback_speak(text, output_file, auto_play)
            
            if not os.path.exists(output_file):
                print(f"[ERROR] Failed to generate speech file")
                return None
            
            print(f"[TTS] ✅ Generated: {output_file}")
            
            if auto_play:
                self.play_audio(output_file)
            
            return output_file
            
        except Exception as e:
            print(f"[ERROR] TTS error: {e}")
            return None
    
    def _fallback_speak(self, text, output_file, auto_play=True):
        """
        Fallback: Use gTTS if Piper not available
        (Note: This won't use the custom voice, just fallback)
        """
        try:
            from gtts import gTTS
            print(f"[TTS] Using gTTS fallback (no custom voice)")
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_file)
            
            if auto_play:
                self.play_audio(output_file)
            
            return output_file
        except Exception as e:
            print(f"[ERROR] Fallback TTS failed: {e}")
            return None
    
    @staticmethod
    def play_audio(file_path, blocking=True):
        """Play audio file using pygame"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            if blocking:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
            print(f"[TTS] Playback finished")
            
        except Exception as e:
            print(f"[ERROR] Audio playback error: {e}")
    
    def set_voice_sample(self, voice_path):
        """Set voice file"""
        if os.path.exists(voice_path):
            self.voice_sample_path = voice_path
            print(f"[TTS] Voice set: {os.path.basename(voice_path)}")
            return True
        else:
            print(f"[ERROR] Voice file not found: {voice_path}")
            return False
    
    def is_ready(self):
        """Always ready - no model loading needed!"""
        return True
