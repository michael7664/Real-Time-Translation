#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime
import speech_recognition as sr
from googletrans import Translator
import sounddevice as sd
import numpy as np
import queue

class GUITranslator:
    def __init__(self, source_lang='it', target_lang='en'):
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.is_listening = False
        
        # Audio setup
        self.audio_queue = queue.Queue()
        self.audio_buffer = bytearray()
        self.sample_rate = 16000
        
        # Create output file
        self.output_file = f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._initialize_output_file()
        
        print(f"GUI Translator initialized: {source_lang} → {target_lang}")
        print(f"Output file: {self.output_file}")
        # Flush output to ensure GUI gets this message
        sys.stdout.flush()
    
    def _initialize_output_file(self):
        """Initialize the output file with header"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"REAL-TIME {self.source_lang.upper()} TO {self.target_lang.upper()} TRANSLATION LOG\n")
            f.write("=" * 60 + "\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Languages: {self.source_lang} → {self.target_lang}\n")
            f.write("=" * 60 + "\n\n")
    
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if self.is_listening:
            # Convert numpy array to bytes (16-bit PCM)
            audio_bytes = (indata * 32767).astype(np.int16).tobytes()
            self.audio_queue.put(audio_bytes)
    
    def start_audio_capture(self):
        """Start capturing audio using sounddevice"""
        self.is_listening = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=1024,
            dtype='float32'
        )
        self.stream.start()
        print("🎤 Audio capture started - listening for Italian audio...")
        sys.stdout.flush()
    
    def process_audio(self):
        """Process audio and return any translations"""
        # Collect audio data
        try:
            while True:
                audio_data = self.audio_queue.get_nowait()
                self.audio_buffer.extend(audio_data)
        except queue.Empty:
            pass
        
        # Check if we have enough audio to process
        if len(self.audio_buffer) < self.sample_rate * 2:  # Need at least 1 second
            return None
        
        try:
            # Convert to AudioData for speech recognition
            audio_data = sr.AudioData(
                bytes(self.audio_buffer), 
                self.sample_rate, 
                2  # 16-bit = 2 bytes per sample
            )
            
            # Clear buffer after processing
            self.audio_buffer.clear()
            
            # Try recognition in source language
            language_code = f'{self.source_lang}-{self.source_lang.upper()}'
            recognized_text = self.recognizer.recognize_google(audio_data, language=language_code)
            
            # Send recognized text to GUI immediately
            print(f"🔊 RECOGNIZED: {recognized_text}")
            sys.stdout.flush()
            
            # Translate to target language
            translated_text = self.translator.translate(recognized_text, src=self.source_lang, dest=self.target_lang).text
            
            # Send translated text to GUI immediately
            print(f"🌐 TRANSLATED: {translated_text}")
            sys.stdout.flush()
            
            # Save to file
            self._save_translation(recognized_text, translated_text)
            
            return {
                'source_text': recognized_text,
                'translated_text': translated_text,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        except sr.UnknownValueError:
            print("🔇 No speech detected in audio")
            sys.stdout.flush()
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Processing error: {e}")
            sys.stdout.flush()
        
        return None
    
    def _save_translation(self, source_text, translated_text):
        """Save translation to file"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"{self.source_lang.upper()}: {source_text}\n")
            f.write(f"{self.target_lang.upper()}: {translated_text}\n")
            f.write("-" * 40 + "\n")
    
    def run_translation_loop(self):
        """Main translation loop for GUI"""
        print("🔄 Starting translation loop...")
        sys.stdout.flush()
        self.start_audio_capture()
        
        try:
            last_process_time = time.time()
            audio_level_check_time = time.time()
            
            while self.is_listening:
                current_time = time.time()
                
                # Show audio level periodically
                if current_time - audio_level_check_time > 2.0:
                    buffer_seconds = len(self.audio_buffer) / (self.sample_rate * 2)
                    print(f"📊 Audio buffer: {buffer_seconds:.1f}s | Queue size: {self.audio_queue.qsize()}")
                    sys.stdout.flush()
                    audio_level_check_time = current_time
                
                # Process audio every 3 seconds
                if current_time - last_process_time > 3.0:
                    translation = self.process_audio()
                    last_process_time = current_time
                
                # Limit buffer size
                if len(self.audio_buffer) > self.sample_rate * 2 * 5:  # Max 5 seconds
                    self.audio_buffer = self.audio_buffer[self.sample_rate * 2:]
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Translation stopped by user")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Error in translation loop: {e}")
            sys.stdout.flush()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        print("✅ Translation stopped")
        sys.stdout.flush()

def main():
    """Main function for command line usage"""
    source_lang = sys.argv[1] if len(sys.argv) > 1 else "it"
    target_lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    
    print(f"🚀 Starting GUI Translator: {source_lang} → {target_lang}")
    sys.stdout.flush()
    
    translator = GUITranslator(source_lang, target_lang)
    
    try:
        translator.run_translation_loop()
    except KeyboardInterrupt:
        print("\n🛑 Stopping translation...")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.stdout.flush()
    finally:
        translator.cleanup()

if __name__ == "__main__":
    main()