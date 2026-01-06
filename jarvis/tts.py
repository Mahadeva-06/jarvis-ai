"""
Text-to-Speech Module with XTTS + brade_clone Voice Reference
Generates dynamic speech using brade_clone.wav as voice reference
Loads XTTS in background for instant responses
"""

import torch
import warnings
import os
import time
import threading
from config import Config

warnings.filterwarnings("ignore")

# Monkeypatch torch.load
_orig_torch_load = torch.load
def _load_wrapper(f, *args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _orig_torch_load(f, *args, **kwargs)
torch.load = _load_wrapper

try:
    from TTS.api import TTS
    XTTS_AVAILABLE = True
except ImportError:
    XTTS_AVAILABLE = False


class TextToSpeech:
    """
    Uses XTTS with brade_clone.wav as voice reference.
    Generates ANY dynamic speech with that voice characteristics.
    Model loads in background - no blocking!
    """
    
    def __init__(self, voice_sample_path=None, use_gpu=None):
        """
        Initialize TTS engine
        
        Args:
            voice_sample_path: brade_clone.wav (voice reference)
            use_gpu: Whether to use GPU
        """
        self.config = Config()
        self.tts_model = None
        self.voice_sample_path = voice_sample_path
        self.use_gpu = use_gpu if use_gpu is not None else torch.cuda.is_available()
        self.model_initialized = False
        self.initialization_thread = None
        
        print("[TTS] Initializing XTTS in background (non-blocking)...")
        print(f"[TTS] Voice Reference: {os.path.basename(voice_sample_path or 'unknown')}")
        # Load in background
        self._init_model_background()
    
    def _init_model_background(self):
        """Initialize XTTS model in background"""
        if not XTTS_AVAILABLE:
            print("[WARNING] XTTS not available")
            return
        
        self.initialization_thread = threading.Thread(
            target=self._initialize_model,
            daemon=True
        )
        self.initialization_thread.start()
    
    def _initialize_model(self):
        """Initialize XTTS"""
        try:
            print("[TTS] Loading XTTS v2 model...")
            self.tts_model = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                gpu=self.use_gpu,
                progress_bar=False
            )
            self.model_initialized = True
            print(f"[TTS] ✅ Ready! Using brade_clone voice reference (GPU: {self.use_gpu})")
        except Exception as e:
            print(f"[ERROR] Failed to load XTTS: {e}")
            self.model_initialized = False
    
    def wait_for_model(self, timeout=300):
        """Wait for model to load"""
        if self.initialization_thread:
            self.initialization_thread.join(timeout=timeout)
    
    def speak(self, text, speaker_wav=None, language='en', speed=1.0, 
              output_file=None, auto_play=True):
        """
        Generate speech using brade_clone voice reference.
        Works for ANY dynamic text!
        
        Args:
            text: ANY text to generate (dynamic!)
            speaker_wav: Voice reference (brade_clone.wav)
            language: Language code
            speed: Speech speed
            output_file: Save audio to file
            auto_play: Play after generation
            
        Returns:
            Path to generated audio file
        """
        # Wait for model if still loading
        if not self.model_initialized:
            print("[TTS] Waiting for XTTS model to load...")
            self.wait_for_model(timeout=120)
        
        if not self.model_initialized:
            print("[ERROR] XTTS model failed to load")
            return None
        
        try:
            # Use brade_clone as voice reference
            voice_wav = speaker_wav or self.voice_sample_path
            
            if not voice_wav or not os.path.exists(voice_wav):
                print(f"[ERROR] Voice reference not found: {voice_wav}")
                return None
            
            if not output_file:
                output_file = f"jarvis_speech_{int(time.time())}.wav"
            
            text_preview = text[:50] + "..." if len(text) > 50 else text
            print(f"[TTS] Generating with brade voice: '{text_preview}'")
            
            # Generate speech using brade_clone as voice reference
            self.tts_model.tts_to_file(
                text=text,
                file_path=output_file,
                speaker_wav=voice_wav,
                language=language,
                speed=speed
            )
            
            print(f"[TTS] Generated: {output_file}")
            
            if auto_play:
                self.play_audio(output_file)
            
            return output_file
            
        except Exception as e:
            print(f"[ERROR] TTS error: {e}")
            return None
    
    @staticmethod
    def play_audio(file_path, blocking=True):
        """Play audio file"""
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
            print(f"[ERROR] Audio playback error: {e}")
    
    def set_voice_sample(self, voice_path):
        """Set voice reference"""
        if os.path.exists(voice_path):
            self.voice_sample_path = voice_path
            print(f"[TTS] Voice Reference: {os.path.basename(voice_path)}")
            return True
        else:
            print(f"[ERROR] Voice file not found: {voice_path}")
            return False
    
    def is_ready(self):
        """Check if model is ready"""
        return self.model_initialized
