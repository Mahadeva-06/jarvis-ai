"""
Configuration Module
Settings and constants for Jarvis
"""

import os


class Config:
    """Configuration settings for Jarvis"""
    
    # Speech Recognition
    LANGUAGE = 'en-US'
    SPEECH_TIMEOUT = 10  # seconds
    
    # Browser
    DEFAULT_SEARCH_URL = 'https://www.google.com'
    
    # System
    SYSTEM_NAME = 'Jarvis'
    VERSION = '1.0.0'
    
    # Paths
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
    VOICES_DIR = os.path.join(PROJECT_ROOT, 'voices')
    DEFAULT_VOICE = os.path.join(VOICES_DIR, 'brade_clone.wav')
    
    # TTS Settings
    TTS_LANGUAGE = 'en'
    TTS_SPEED = 1.0
    TTS_USE_GPU = True
    
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
