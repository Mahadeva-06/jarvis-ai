"""
Speech-to-Text Module
Offline speech recognition using available libraries
"""

import speech_recognition as sr
from config import Config


class SpeechToText:
    """Handles offline speech-to-text conversion"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.config = Config()
        self.microphone = sr.Microphone()
        
    def listen(self, timeout=10):
        """
        Listen to microphone input and convert to text
        
        Args:
            timeout: Timeout in seconds for listening
            
        Returns:
            str: Recognized text or None if recognition failed
        """
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Try to recognize using Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='en-US')
            return text.lower()
            
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def listen_offline(self):
        """
        Offline speech-to-text (requires local model)
        Placeholder for offline implementation
        """
        pass
