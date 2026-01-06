"""
🧠 STAGE 1: VOICE CLONING (XTTS ONLY)

This script ONLY uses XTTS to clone a voice.
After cloning, the voice file is saved and XTTS is no longer needed.

Workflow:
1. Provide source voice (speaker.wav, audio.mp3, etc.)
2. XTTS generates a clean voice profile
3. Save as voices/custom_voice.wav
4. Jarvis uses that wav file forever (no XTTS needed at runtime)

This is the CORRECT separation:
✅ XTTS = Voice Factory (used ONCE)
✅ Jarvis = Voice Consumer (uses saved wav)
"""

import os
import torch
import warnings

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
except ImportError:
    print("[ERROR] TTS library not found. Install: pip install TTS")
    exit()


class VoiceCloner:
    """Clone a voice ONCE using XTTS"""
    
    def __init__(self):
        self.voices_dir = "jarvis/voices"
        self.use_gpu = torch.cuda.is_available()
        self.tts_model = None
        print(f"[CLONER] GPU Available: {self.use_gpu}")
    
    def clone_voice(self, source_audio, output_name, reference_text="Hello, I am Jarvis, your personal AI assistant."):
        """
        Clone a voice ONCE
        
        Args:
            source_audio: Path to source voice (mp3, wav, etc.)
            output_name: Name for saved voice (e.g., 'custom_voice')
            reference_text: Text to generate as voice reference
        """
        if not os.path.exists(source_audio):
            print(f"[ERROR] Source audio not found: {source_audio}")
            return False
        
        if not os.path.exists(self.voices_dir):
            os.makedirs(self.voices_dir)
            print(f"[CLONER] Created {self.voices_dir}/")
        
        # Load XTTS (only done ONCE per cloning)
        print("[CLONER] Loading XTTS v2 model...")
        try:
            self.tts_model = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                gpu=self.use_gpu,
                progress_bar=True
            )
        except Exception as e:
            print(f"[ERROR] Failed to load XTTS: {e}")
            return False
        
        # Generate voice profile
        output_path = os.path.join(self.voices_dir, f"{output_name}.wav")
        
        print(f"\n[CLONER] Cloning voice from: {source_audio}")
        print(f"[CLONER] Output: {output_path}")
        print(f"[CLONER] Reference text: {reference_text}")
        
        try:
            self.tts_model.tts_to_file(
                text=reference_text,
                file_path=output_path,
                speaker_wav=source_audio,
                language="en"
            )
            
            print(f"\n✅ VOICE CLONED SUCCESSFULLY!")
            print(f"📁 Saved: {output_path}")
            print(f"\n🎯 Now Jarvis can use this voice forever (no XTTS needed):")
            print(f"   jarvis_tts.set_voice_sample('{output_path}')")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Cloning failed: {e}")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 VOICE CLONING STAGE 1 (XTTS ONLY FOR CLONING)")
    print("=" * 60)
    
    cloner = VoiceCloner()
    
    # Example: Clone brade voice
    source = "GTTS/voices/brade_clone.mp3"  # Or any audio file
    
    if os.path.exists(source):
        cloner.clone_voice(
            source_audio=source,
            output_name="brade_clone",
            reference_text="Hello, I am Jarvis, your personal AI assistant."
        )
    else:
        print(f"[INFO] Example file not found: {source}")
        print("[INFO] Usage:")
        print('  cloner = VoiceCloner()')
        print('  cloner.clone_voice("path/to/voice.mp3", "my_voice")')
        print("\nThen Jarvis will use: jarvis/voices/my_voice.wav")
