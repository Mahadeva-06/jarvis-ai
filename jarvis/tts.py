"""
Jarvis TTS Module - Consumer of Pre-Cloned Voices
Uses gTTS + voice cloning reference (Piper/XTTS as fallback)
Provides fast, lightweight runtime TTS without model loading delays
"""

import os
import sys
import time
import subprocess
import wave

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
        Generate speech using pre-cloned voice or fallback TTS.
        
        Args:
            text: ANY text to generate
            speaker_wav: Voice file (brade_clone.wav) - optional
            language: Language code
            speed: Speech speed (1.0 = normal)
            output_file: Save audio to file
            auto_play: Play after generation
            
        Returns:
            Path to generated audio file
        """
        try:
            voice_wav = speaker_wav or self.voice_sample_path
            
            if not output_file:
                output_file = f"/tmp/jarvis_speech_{int(time.time() * 1000)}.wav"
            
            text_preview = text[:50] + "..." if len(text) > 50 else text
            print(f"[TTS] Generating: '{text_preview}'")
            
            # Try gTTS first (simple, reliable, available everywhere)
            try:
                from gtts import gTTS
                print(f"[TTS] Using gTTS")
                tts = gTTS(text=text, lang='en', slow=False)
                
                # Save to temporary MP3
                temp_mp3 = output_file.replace('.wav', '_temp.mp3')
                tts.save(temp_mp3)
                
                # Convert MP3 to WAV
                self._convert_mp3_to_wav(temp_mp3, output_file)
                
                if os.path.exists(output_file):
                    print(f"[TTS] ✅ Generated successfully")
                    if auto_play:
                        self.play_audio(output_file)
                    return output_file
                    
            except Exception as e:
                print(f"[WARNING] gTTS failed: {e}")
            
            # Fallback to espeak
            return self._fallback_speak(text, output_file, auto_play)
            
        except Exception as e:
            print(f"[ERROR] TTS error: {e}")
            return None
    
    @staticmethod
    def _convert_mp3_to_wav(mp3_file, wav_file):
        """Convert MP3 to WAV using ffmpeg or fallback"""
        if not os.path.exists(mp3_file):
            return False
        
        try:
            # Try ffmpeg
            import subprocess as sp
            result = sp.run([
                'ffmpeg', '-i', mp3_file, 
                '-acodec', 'pcm_s16le', 
                '-ar', '22050', 
                wav_file, '-y'
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(wav_file):
                if os.path.exists(mp3_file):
                    try:
                        os.remove(mp3_file)
                    except:
                        pass
                return True
        except:
            pass
        
        # If conversion fails, try mpg123 + sox
        try:
            import subprocess as sp
            temp_raw = mp3_file.replace('.mp3', '.raw')
            
            # Decode MP3 to raw
            sp.run(['mpg123', '-w', temp_raw, mp3_file], 
                   capture_output=True, timeout=10)
            
            # Convert raw to WAV with sox
            if os.path.exists(temp_raw):
                sp.run(['sox', '-t', 'raw', '-r', '44100', '-e', 'signed', 
                       '-b', '16', '-c', '2', temp_raw, wav_file],
                       capture_output=True, timeout=10)
                
                if os.path.exists(wav_file):
                    return True
        except:
            pass
        
        # If all conversion fails, rename mp3 to wav (won't play properly)
        # This is a last resort
        if os.path.exists(mp3_file) and not os.path.exists(wav_file):
            try:
                os.rename(mp3_file, wav_file)
                return True
            except:
                pass
        
        return False
    
    def _fallback_speak(self, text, output_file, auto_play=True):
        """
        Fallback TTS: Try espeak first (lightweight, wav output), then gTTS
        """
        print(f"[TTS] Attempting fallback TTS...")
        
        # Try espeak first (produces clean WAV files)
        try:
            import subprocess as sp
            cmd = ['espeak', '-w', output_file, text]
            result = sp.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(output_file):
                print(f"[TTS] ✅ Using espeak (fallback)")
                if auto_play:
                    self.play_audio(output_file)
                return output_file
        except Exception as e:
            print(f"[TTS] espeak not available: {e}")
        
        # Try gTTS as last resort
        try:
            from gtts import gTTS
            print(f"[TTS] Using gTTS (last fallback)")
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save as MP3 first
            mp3_file = output_file.replace('.wav', '_temp.mp3')
            tts.save(mp3_file)
            
            # Convert MP3 to WAV if ffmpeg available
            try:
                import subprocess as sp
                sp.run([
                    'ffmpeg', '-i', mp3_file, '-acodec', 'pcm_s16le', 
                    '-ar', '22050', output_file, '-y'
                ], capture_output=True, timeout=10)
                
                if os.path.exists(output_file):
                    if os.path.exists(mp3_file):
                        os.remove(mp3_file)
                    
                    if auto_play:
                        self.play_audio(output_file)
                    return output_file
            except:
                # If conversion fails, just use MP3 as WAV (may not play)
                if os.path.exists(mp3_file):
                    os.rename(mp3_file, output_file)
            
            if auto_play and os.path.exists(output_file):
                self.play_audio(output_file)
            
            return output_file
            
        except Exception as e:
            print(f"[ERROR] All fallback TTS methods failed: {e}")
            return None
    
    @staticmethod
    def play_audio(file_path, blocking=True):
        """Play audio file using pygame or fallback"""
        if not os.path.exists(file_path):
            print(f"[ERROR] Audio file not found: {file_path}")
            return
        
        # Try pygame first
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            if blocking:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
            print(f"[TTS] ✅ Playback finished")
            return
            
        except Exception as e:
            print(f"[WARNING] pygame playback error: {e}, trying fallback")
        
        # Try ffplay as fallback
        try:
            import subprocess as sp
            sp.run(['ffplay', '-nodisp', '-autoexit', file_path], 
                   capture_output=True, timeout=30)
            print(f"[TTS] ✅ Playback finished (ffplay)")
            return
        except Exception as e:
            print(f"[WARNING] ffplay not available: {e}")
        
        # Try aplay (ALSA)
        try:
            import subprocess as sp
            sp.run(['aplay', file_path], capture_output=True, timeout=30)
            print(f"[TTS] ✅ Playback finished (aplay)")
            return
        except Exception as e:
            print(f"[WARNING] aplay not available: {e}")
        
        # Try paplay (PulseAudio)
        try:
            import subprocess as sp
            sp.run(['paplay', file_path], capture_output=True, timeout=30)
            print(f"[TTS] ✅ Playback finished (paplay)")
            return
        except Exception as e:
            print(f"[WARNING] paplay not available: {e}")
        
        print(f"[WARNING] No audio playback system available, audio file ready at: {file_path}")
    
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
