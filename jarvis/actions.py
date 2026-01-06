"""
Actions Module
Handles laptop control commands and actions
"""

import os
import subprocess
import webbrowser
from config import Config


class Actions:
    """Executes various system and application commands"""
    
    def __init__(self):
        self.config = Config()
        self.commands = {
            'open browser': self.open_browser,
            'play music': self.play_music,
            'shutdown': self.shutdown,
            'restart': self.restart,
            'open': self.open_application,
            'volume': self.control_volume,
            'screenshot': self.take_screenshot,
        }
    
    def process_command(self, text):
        """
        Process voice commands and execute actions
        
        Args:
            text: Voice command text
        """
        for command, action in self.commands.items():
            if command in text:
                action(text)
                return
        
        print("Command not recognized")
    
    def open_browser(self, text):
        """Open web browser"""
        url = self.config.DEFAULT_SEARCH_URL
        if 'google' in text:
            webbrowser.open('https://www.google.com')
        else:
            webbrowser.open(url)
        print("🌐 Opening browser...")
    
    def play_music(self, text):
        """Play music"""
        print("🎵 Playing music...")
        # Implementation depends on media player
    
    def shutdown(self, text):
        """Shutdown the system"""
        print("⏻️  Shutting down system in 30 seconds...")
        if os.name == 'nt':
            os.system('shutdown /s /t 30')
        else:
            os.system('shutdown -h +1')
    
    def restart(self, text):
        """Restart the system"""
        print("🔄 Restarting system...")
        if os.name == 'nt':
            os.system('shutdown /r /t 30')
        else:
            os.system('shutdown -r +1')
    
    def open_application(self, text):
        """Open an application"""
        print(f"Opening application from command: {text}")
        # Extract app name and open it
    
    def control_volume(self, text):
        """Control system volume"""
        print("🔊 Adjusting volume...")
    
    def take_screenshot(self, text):
        """Take a screenshot"""
        print("📸 Screenshot taken")
        try:
            import pyautogui
            pyautogui.screenshot(f'screenshot_{os.getpid()}.png')
        except ImportError:
            print("pyautogui not installed")
