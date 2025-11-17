import pygame
import sys
import time
from datetime import datetime
import speech_recognition as sr
from googletrans import Translator
import sounddevice as sd
import numpy as np
import queue
import io
import os

def __init__(self, source_lang='it', target_lang='en'):
    self.config = Config()
    
    # Override language settings
    self.config.SOURCE_LANGUAGE = source_lang
    self.config.TARGET_LANGUAGE = target_lang
    
    # Initialize components with config
    self.audio_capture = AudioCapture(
        rate=self.config.SAMPLE_RATE,
        chunk_size=self.config.CHUNK_SIZE,
        channels=self.config.CHANNELS
    )
    self.speech_to_text = SpeechToText(
        language=f'{self.config.SOURCE_LANGUAGE}-{self.config.SOURCE_LANGUAGE.upper()}'
    )
    self.translator = TextTranslator(
        src_lang=self.config.SOURCE_LANGUAGE,
        dest_lang=self.config.TARGET_LANGUAGE
    )


class FixedTranslator:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.translated_lines = []
        self.debug_messages = []
        self.is_listening = False
        self.saved_translations = []
        self.current_paragraph = []
        self.last_translation_time = time.time()
        
        # Create output file
        self.output_file = f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._initialize_output_file()
        
        # Audio queue for sounddevice
        self.audio_queue = queue.Queue()
        self.audio_buffer = bytearray()
        
        # Pygame for display
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption("Fixed Translator - Italian to English")
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Start audio capture
        self.start_audio_capture()
        
    def _initialize_output_file(self):
        """Initialize the output file with header"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("REAL-TIME ITALIAN TO ENGLISH TRANSLATION LOG\n")
            f.write("=" * 60 + "\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
        self.add_debug(f"Output file created: {self.output_file}")
    
    def _save_to_file(self, text, translation, is_new_paragraph=False):
        """Save translation to file with structured formatting"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        with open(self.output_file, 'a', encoding='utf-8') as f:
            if is_new_paragraph:
                f.write("\n" + "─" * 50 + "\n")
                f.write(f"PARAGRAPH START: {timestamp}\n")
                f.write("─" * 50 + "\n")
            
            f.write(f"[{timestamp}]\n")
            f.write(f"Italian: {text}\n")
            f.write(f"English: {translation}\n")
            f.write("-" * 40 + "\n")
        
        # Also save to memory for display
        self.saved_translations.append({
            'timestamp': timestamp,
            'italian': text,
            'english': translation
        })
    
    def _should_start_new_paragraph(self, current_time):
        """Determine if we should start a new paragraph based on timing"""
        if not self.current_paragraph:
            return True
        
        # If more than 10 seconds since last translation, start new paragraph
        time_gap = current_time - self.last_translation_time
        return time_gap > 10.0
    
    def _is_complete_sentence(self, text):
        """Check if text looks like a complete sentence"""
        # Simple heuristic: ends with sentence-ending punctuation
        return any(text.strip().endswith(punct) for punct in ['.', '!', '?'])
    
    def add_debug(self, message):
        """Add debug message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_messages.insert(0, f"[{timestamp}] {message}")
        if len(self.debug_messages) > 10:
            self.debug_messages = self.debug_messages[:10]
        print(message)
    
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
            samplerate=16000,
            channels=1,
            callback=self.audio_callback,
            blocksize=1024,
            dtype='float32'
        )
        self.stream.start()
        self.add_debug("Audio capture started with sounddevice")
    
    def process_audio_buffer(self):
        """Process accumulated audio data"""
        if len(self.audio_buffer) < 16000 * 2:  # Need at least 1 second of audio
            return
        
        try:
            # Convert to AudioData for speech recognition
            audio_data = sr.AudioData(
                bytes(self.audio_buffer), 
                16000, 
                2  # 16-bit = 2 bytes per sample
            )
            
            # Clear buffer after processing
            self.audio_buffer.clear()
            
            # Try Italian recognition
            italian_text = self.recognizer.recognize_google(audio_data, language='it-IT')
            self.add_debug(f"SUCCESS: Recognized Italian: {italian_text}")
            
            # Translate
            translated = self.translator.translate(italian_text, src='it', dest='en')
            self.add_debug(f"SUCCESS: Translated: {translated.text}")
            
            # Determine if this should be a new paragraph
            current_time = time.time()
            is_new_paragraph = self._should_start_new_paragraph(current_time)
            
            # Save to file
            self._save_to_file(italian_text, translated.text, is_new_paragraph)
            
            # Update paragraph tracking
            if is_new_paragraph and self.current_paragraph:
                self.current_paragraph = []  # Start new paragraph
            
            self.current_paragraph.append(translated.text)
            self.last_translation_time = current_time
            
            # Add to display
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.translated_lines.insert(0, f"[{timestamp}] {translated.text}")
            if len(self.translated_lines) > 5:
                self.translated_lines = self.translated_lines[:5]
                
        except sr.UnknownValueError:
            self.add_debug("No Italian speech detected in audio")
        except sr.RequestError as e:
            self.add_debug(f"Speech recognition error: {e}")
        except Exception as e:
            self.add_debug(f"Processing error: {e}")
    
    def update_display(self):
        """Update the display"""
        self.screen.fill((0, 0, 0))
        
        # Title
        title = self.font.render("Fixed Translator - Italian to English (Real-time)", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # File info
        file_info = self.small_font.render(f"Saving to: {self.output_file}", True, (128, 255, 255))
        self.screen.blit(file_info, (20, 45))
        
        # Instructions
        instructions = [
            "REAL-TIME TRANSLATION ACTIVE - SPEAK ITALIAN",
            "The system is continuously listening and translating",
            "Make sure Italian audio is playing through your speakers",
            f"Translations are being saved to: {self.output_file}"
        ]
        
        y_offset = 70
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (255, 255, 0))
            self.screen.blit(text, (20, y_offset))
            y_offset += 20
        
        # Translated text
        y_offset += 20
        title = self.font.render("LIVE TRANSLATIONS:", True, (0, 255, 0))
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        if not self.translated_lines:
            text = self.font.render("Listening for Italian audio...", True, (128, 128, 128))
            self.screen.blit(text, (20, y_offset))
        else:
            for i, line in enumerate(self.translated_lines):
                text = self.font.render(line, True, (255, 255, 0))
                self.screen.blit(text, (20, y_offset + i * 25))
        
        # Debug messages
        y_offset = 300
        title = self.font.render("STATUS MESSAGES:", True, (255, 0, 0))
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        for i, message in enumerate(self.debug_messages):
            color = (255, 100, 100) if "ERROR" in message else (100, 255, 100) if "SUCCESS" in message else (200, 200, 200)
            text = self.small_font.render(message, True, color)
            self.screen.blit(text, (20, y_offset + i * 18))
        
        # Stats
        stats_y = 550
        stats = [
            f"Translations saved: {len(self.saved_translations)}",
            f"Current paragraph: {len(self.current_paragraph)} sentences",
            f"Audio buffer: {len(self.audio_buffer) / (16000 * 2):.1f}s"
        ]
        
        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, (128, 128, 255))
            self.screen.blit(text, (20 + i * 250, stats_y))
        
        # Controls
        controls = self.small_font.render("Press Q to quit | S to show file location", True, (128, 128, 255))
        self.screen.blit(controls, (20, 570))
        
        pygame.display.flip()
    
    def show_file_location(self):
        """Show where the file is saved"""
        file_path = os.path.abspath(self.output_file)
        self.add_debug(f"Translation file: {file_path}")
        return file_path
    
    def run(self):
        """Main loop"""
        self.add_debug("Fixed translator started with sounddevice backend")
        self.add_debug("Real-time translation active - speaking Italian should be translated automatically")
        self.add_debug(f"Translations will be saved to: {self.output_file}")
        
        running = True
        last_process_time = time.time()
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_s:
                        file_path = self.show_file_location()
                        self.add_debug(f"File location: {file_path}")
            
            # Collect audio data
            try:
                while True:  # Empty the queue
                    audio_data = self.audio_queue.get_nowait()
                    self.audio_buffer.extend(audio_data)
            except queue.Empty:
                pass
            
            # Process audio every 3 seconds
            current_time = time.time()
            if current_time - last_process_time > 3.0 and len(self.audio_buffer) > 0:
                self.process_audio_buffer()
                last_process_time = current_time
            
            # Limit buffer size
            if len(self.audio_buffer) > 16000 * 2 * 5:  # Max 5 seconds
                self.audio_buffer = self.audio_buffer[16000 * 2:]  # Remove oldest second
            
            self.update_display()
            pygame.time.delay(50)
        
        # Save final summary
        self._save_final_summary()
        
        # Cleanup
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        pygame.quit()
    
    def _save_final_summary(self):
        """Save a summary when the application closes"""
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write("SESSION SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total translations: {len(self.saved_translations)}\n")
            f.write("=" * 60 + "\n")
        
        self.add_debug(f"Final summary saved to {self.output_file}")
        print(f"\n=== TRANSLATION COMPLETE ===")
        print(f"All translations saved to: {os.path.abspath(self.output_file)}")
        print(f"Total translations recorded: {len(self.saved_translations)}")

if __name__ == "__main__":
    translator = FixedTranslator()
    translator.run()