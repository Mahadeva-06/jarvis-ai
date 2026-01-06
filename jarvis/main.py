"""
Jarvis - AI Voice Assistant
Entry point for the application
"""

import sys
from stt import SpeechToText
from actions import Actions
from config import Config


def main():
    """Main entry point for Jarvis"""
    config = Config()
    stt = SpeechToText()
    actions = Actions()
    
    print("🎤 Jarvis initialized. Listening...")
    
    try:
        while True:
            # Listen for speech input
            text = stt.listen()
            
            if text:
                print(f"You said: {text}")
                
                # Process the command
                actions.process_command(text)
                
    except KeyboardInterrupt:
        print("\n👋 Jarvis shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
