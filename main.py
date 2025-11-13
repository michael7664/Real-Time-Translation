import pygame
import sys
import time
from datetime import datetime
from config import Config
from audio_capture import AudioCapture
from speech_to_text import SpeechToText
from translator import TextTranslator

class TeamsTranslator:
    def __init__(self, config):
        self.config = config
        
        # Initialize components
        try:
            self.audio_capture = AudioCapture(
                rate=config.SAMPLE_RATE,
                chunk_size=config.CHUNK_SIZE,
                channels=config.CHANNELS
            )
        except ImportError as e:
            print(f"Audio capture initialization failed: {e}")
            print("Please install sounddevice: pip install sounddevice")
            sys.exit(1)
            
        self.speech_to_text = SpeechToText(language=f'{config.SOURCE_LANGUAGE}-{config.SOURCE_LANGUAGE.upper()}')
        self.translator = TextTranslator(
            src_lang=config.SOURCE_LANGUAGE,
            dest_lang=config.TARGET_LANGUAGE
        )
        
        # For displaying translations
        self.translated_lines = []
        self.last_audio_time = time.time()
        self.audio_buffer_duration = 0
        
        # Pygame for display
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 500))
        pygame.display.set_caption("Teams Real-time Translator")
        self.font = pygame.font.Font(None, self.config.FONT_SIZE)
        self.small_font = pygame.font.Font(None, 18)
        
    def start(self):
        """Start the translation process"""
        print("Starting Teams Real-time Translator...")
        print("Press 'Q' to quit or close the window")
        print("Make sure Teams audio is playing and microphone can capture it")
        
        try:
            self.audio_capture.start_capture()
            self._main_loop()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            self.cleanup()
            
    def _main_loop(self):
        """Main application loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
            
            # Process audio
            self._process_audio()
            
            # Update display
            self._update_display()
            
            # Cap the frame rate
            pygame.time.delay(50)
            
    def _process_audio(self):
        """Process audio data and perform translation"""
        audio_data = self.audio_capture.get_audio_data()
        
        if audio_data:
            self.speech_to_text.add_audio_data(audio_data)
            self.last_audio_time = time.time()
            self.audio_buffer_duration += len(audio_data) / (self.config.SAMPLE_RATE * 2)
            
        # Process speech recognition periodically
        current_time = time.time()
        if current_time - self.last_audio_time > self.config.PHRASE_TIMEOUT and self.audio_buffer_duration > 1.0:
            print("Processing audio...")
            recognized_text = self.speech_to_text.recognize_speech()
            self.audio_buffer_duration = 0
            
            if recognized_text:
                print(f"Recognized (Italian): {recognized_text}")
                
                # Translate the text
                translated_text = self.translator.translate_text(recognized_text)
                print(f"Translated (English): {translated_text}")
                
                # Add to display lines
                timestamp = datetime.now().strftime("%H:%M:%S")
                display_text = f"[{timestamp}] {translated_text}"
                self.translated_lines.insert(0, display_text)
                
                # Keep only recent lines
                if len(self.translated_lines) > self.config.MAX_DISPLAY_LINES:
                    self.translated_lines = self.translated_lines[:self.config.MAX_DISPLAY_LINES]
                    
                self.last_audio_time = current_time
    
    def _update_display(self):
        """Update the display with translated text"""
        self.screen.fill((0, 0, 0))  # Black background
        
        # Display title
        title = self.font.render("Teams Real-time Translation (Italian → English)", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # Display status
        status = self.small_font.render("Status: Listening... | Buffer: {:.1f}s".format(self.audio_buffer_duration), True, (0, 255, 0))
        self.screen.blit(status, (20, 50))
        
        # Display translated lines
        y_offset = 80
        if not self.translated_lines:
            placeholder = self.font.render("Waiting for Italian audio...", True, (128, 128, 128))
            self.screen.blit(placeholder, (20, y_offset))
        else:
            for i, line in enumerate(self.translated_lines):
                text_surface = self.font.render(line, True, (255, 255, 0))  # Yellow text
                self.screen.blit(text_surface, (20, y_offset + i * 30))
            
        # Display instructions
        instructions = self.small_font.render("Press 'Q' to quit | Make sure Teams audio is audible", True, (128, 128, 128))
        self.screen.blit(instructions, (20, 450))
        
        pygame.display.flip()
        
    def cleanup(self):
        """Clean up resources"""
        self.audio_capture.stop_capture()
        pygame.quit()
        print("Translation stopped.")

def main():
    config = Config()
    translator = TeamsTranslator(config)
    translator.start()

if __name__ == "__main__":
    main()