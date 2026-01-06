"""
Configuration Module for Jarvis

🧠 ARCHITECTURE:
- STAGE 1 (Voice Cloning): Use XTTS ONCE → save voice profile (brade_clone.wav)
- STAGE 2 (Jarvis Speaking): Use Piper TTS with saved voice file

✅ SEPARATION OF CONCERNS:
  XTTS = Voice Factory (used ONCE for cloning)
  Piper = Voice Engine (lightweight TTS at runtime)
  Jarvis = Voice Consumer (uses pre-cloned voices)
"""

import os


class Config:
    """Configuration settings for Jarvis - Clean 2-Stage Voice System"""
    
    # Speech Recognition
    LANGUAGE = 'en-US'
    SPEECH_TIMEOUT = 10  # seconds
    
    # Browser
    DEFAULT_SEARCH_URL = 'https://www.google.com'
    
    # System
    SYSTEM_NAME = 'Jarvis'
    VERSION = '2.0.0'  # Updated with new architecture
    
    # Paths
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
    VOICES_DIR = os.path.join(PROJECT_ROOT, 'voices')
    DEFAULT_VOICE = os.path.join(VOICES_DIR, 'brade_clone.wav')
    
    # TTS Settings (Piper - Lightweight)
    TTS_LANGUAGE = 'en'
    TTS_SPEED = 1.0
    TTS_USE_GPU = False  # Piper doesn't need GPU
    
    # Logging
    DEBUG = True
    
    def __init__(self):
        """Initialize configuration"""
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(self.VOICES_DIR, exist_ok=True)
    
    @staticmethod
    def get_config():
        """Get configuration instance"""
        return Config()
