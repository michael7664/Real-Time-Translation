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

class StandaloneTranslator:
    def __init__(self, source_lang='it', target_lang='en', output_folder=""):
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.is_listening = False
        
        # Audio setup
        self.audio_queue = queue.Queue()
        self.audio_buffer = bytearray()
        self.sample_rate = 16000
        
        # Paragraph tracking
        self.current_paragraph = []
        self.last_translation_time = time.time()
        self.paragraph_counter = 1
        
        # Create output directory and file
        self.output_dir = self._get_output_directory(output_folder)
        self.output_file = self._create_output_file(output_folder)
        
        print(f"🚀 Standalone Translator initialized: {source_lang} → {target_lang}")
        print(f"📁 Output file: {self.output_file}")
        sys.stdout.flush()
    
    def _get_output_directory(self, custom_folder=""):
        """Get the output directory - use custom folder if provided, else default"""
        if custom_folder and os.path.exists(custom_folder):
            output_dir = custom_folder
            print(f"📂 Using custom output folder: {output_dir}")
        else:
            # Fallback to default location
            home_dir = os.path.expanduser("~")
            output_dir = os.path.join(home_dir, "output")
            if custom_folder:
                print(f"⚠️  Custom folder not found: {custom_folder}, using default: {output_dir}")
            else:
                print(f"📂 Using default output folder: {output_dir}")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def _create_output_file(self, custom_folder=""):
        """Create output file path with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"translations_{timestamp}.txt"
        output_dir = self._get_output_directory(custom_folder)
        return os.path.join(output_dir, filename)
    
    def _initialize_output_file(self):
        """Initialize the output file with header"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"REAL-TIME {self.source_lang.upper()} TO {self.target_lang.upper()} TRANSLATION LOG\n")
            f.write("=" * 60 + "\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Languages: {self.source_lang} → {self.target_lang}\n")
            f.write(f"File: {self.output_file}\n")
            f.write("=" * 60 + "\n\n")
    
    def _should_start_new_paragraph(self, current_time):
        """Determine if we should start a new paragraph based on timing"""
        if not self.current_paragraph:
            return True
        
        # If more than 15 seconds since last translation, start new paragraph
        time_gap = current_time - self.last_translation_time
        return time_gap > 15.0
    
    def _is_complete_sentence(self, text):
        """Check if text looks like a complete sentence"""
        # Simple heuristic: ends with sentence-ending punctuation
        text = text.strip()
        return any(text.endswith(punct) for punct in ['.', '!', '?', '。', '！', '？'])
    
    def _save_translation_with_paragraphs(self, source_text, translated_text):
        """Save translation to file with paragraph formatting"""
        current_time = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Check if we should start a new paragraph
        should_start_new_paragraph = self._should_start_new_paragraph(current_time)
        
        with open(self.output_file, 'a', encoding='utf-8') as f:
            if should_start_new_paragraph and self.current_paragraph:
                # Save the completed paragraph
                f.write("\n" + "─" * 50 + "\n")
                f.write(f"PARAGRAPH {self.paragraph_counter} COMPLETE\n")
                f.write("─" * 50 + "\n")
                for sentence in self.current_paragraph:
                    f.write(f"• {sentence}\n")
                f.write("─" * 50 + "\n\n")
                
                # Start new paragraph
                self.current_paragraph = []
                self.paragraph_counter += 1
            
            if should_start_new_paragraph:
                f.write("\n" + "═" * 50 + "\n")
                f.write(f"PARAGRAPH {self.paragraph_counter} START: {timestamp}\n")
                f.write("═" * 50 + "\n")
            
            # Save the current translation
            f.write(f"[{timestamp}]\n")
            f.write(f"{self.source_lang.upper()}: {source_text}\n")
            f.write(f"{self.target_lang.upper()}: {translated_text}\n")
            f.write("-" * 40 + "\n")
            
            # Add to current paragraph if it's a complete sentence
            if self._is_complete_sentence(translated_text):
                self.current_paragraph.append(translated_text)
        
        # Update timing
        self.last_translation_time = current_time
        
        # Debug info
        print(f"📝 Paragraph {self.paragraph_counter}, Sentences: {len(self.current_paragraph)}")
        print(f"💾 Saved to: {self.output_file}")
        sys.stdout.flush()
    
    def _save_final_paragraph(self):
        """Save any remaining sentences in the current paragraph when stopping"""
        if self.current_paragraph:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "─" * 50 + "\n")
                f.write(f"PARAGRAPH {self.paragraph_counter} COMPLETE (FINAL)\n")
                f.write("─" * 50 + "\n")
                for sentence in self.current_paragraph:
                    f.write(f"• {sentence}\n")
                f.write("─" * 50 + "\n\n")
            
            print(f"💾 Saved final paragraph with {len(self.current_paragraph)} sentences")
            sys.stdout.flush()
    
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if self.is_listening:
            # Convert numpy array to bytes (16-bit PCM)
            audio_bytes = (indata * 32767).astype(np.int16).tobytes()
            self.audio_queue.put(audio_bytes)
    
    def start_audio_capture(self):
        """Start capturing audio using sounddevice"""
        self.is_listening = True
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=1024,
                dtype='float32'
            )
            self.stream.start()
            print("🎤 Audio capture started - listening for audio...")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Failed to start audio capture: {e}")
            sys.stdout.flush()
            raise
    
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
            print(f"🔍 Attempting speech recognition for {language_code}...")
            sys.stdout.flush()
            
            recognized_text = self.recognizer.recognize_google(audio_data, language=language_code)
            
            # Send recognized text to GUI immediately
            print(f"🔊 RECOGNIZED_{self.source_lang.upper()}: {recognized_text}")
            sys.stdout.flush()
            
            # Translate to target language
            print("🔄 Translating...")
            sys.stdout.flush()
            translated_text = self.translator.translate(recognized_text, src=self.source_lang, dest=self.target_lang).text
            
            # Send translated text to GUI immediately
            print(f"🌐 TRANSLATED_{self.target_lang.upper()}: {translated_text}")
            sys.stdout.flush()
            
            # Save to file with paragraph formatting
            self._save_translation_with_paragraphs(recognized_text, translated_text)
            
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
    
    def run_translation_loop(self):
        """Main translation loop for GUI"""
        print("🔄 Starting translation loop...")
        # Initialize the file here to ensure it's created when translation starts
        self._initialize_output_file()
        sys.stdout.flush()
        self.start_audio_capture()
        
        try:
            last_process_time = time.time()
            audio_level_check_time = time.time()
            consecutive_no_audio = 0
            
            while self.is_listening:
                current_time = time.time()
                
                # Show audio level periodically
                if current_time - audio_level_check_time > 2.0:
                    buffer_seconds = len(self.audio_buffer) / (self.sample_rate * 2)
                    queue_size = self.audio_queue.qsize()
                    print(f"📊 Audio buffer: {buffer_seconds:.1f}s | Queue: {queue_size}")
                    sys.stdout.flush()
                    
                    # Check if we're getting any audio data
                    if buffer_seconds < 0.1 and queue_size == 0:
                        consecutive_no_audio += 1
                        if consecutive_no_audio >= 3:
                            print("⚠️  No audio detected. Check microphone and volume!")
                            sys.stdout.flush()
                    else:
                        consecutive_no_audio = 0
                    
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
        # Save any remaining paragraph
        self._save_final_paragraph()
        
        # Add final summary
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write("SESSION SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total paragraphs: {self.paragraph_counter}\n")
            f.write(f"File location: {self.output_file}\n")
            f.write("=" * 60 + "\n")
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        print(f"✅ Translation stopped. File saved to: {self.output_file}")
        sys.stdout.flush()

def main():
    """Main function for command line usage"""
    source_lang = sys.argv[1] if len(sys.argv) > 1 else "it"
    target_lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    output_folder = sys.argv[3] if len(sys.argv) > 3 else ""
    
    print(f"🚀 Starting Standalone Translator: {source_lang} → {target_lang}")
    if output_folder:
        print(f"📁 Custom output folder: {output_folder}")
    sys.stdout.flush()
    
    translator = StandaloneTranslator(source_lang, target_lang, output_folder)
    
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