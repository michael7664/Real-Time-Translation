import pygame
import sys
import time
from datetime import datetime
import speech_recognition as sr
from googletrans import Translator

class DebugTranslator:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.translated_lines = []
        self.debug_messages = []
        
        # Pygame for display
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption("Debug Translator")
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
    def add_debug(self, message):
        """Add debug message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_messages.insert(0, f"[{timestamp}] {message}")
        if len(self.debug_messages) > 10:
            self.debug_messages = self.debug_messages[:10]
        print(message)
    
    def test_microphone(self):
        """Test microphone with different settings"""
        self.add_debug("Testing microphone...")
        try:
            with sr.Microphone() as source:
                self.add_debug("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.add_debug("Listening for Italian audio...")
                
                # Listen with longer timeout
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                self.add_debug("Audio captured, processing...")
                
                # Try Italian recognition
                try:
                    italian_text = self.recognizer.recognize_google(audio, language='it-IT')
                    self.add_debug(f"SUCCESS: Recognized Italian: {italian_text}")
                    
                    # Translate
                    translated = self.translator.translate(italian_text, src='it', dest='en')
                    self.add_debug(f"SUCCESS: Translated: {translated.text}")
                    
                    # Add to display
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.translated_lines.insert(0, f"[{timestamp}] {translated.text}")
                    if len(self.translated_lines) > 5:
                        self.translated_lines = self.translated_lines[:5]
                        
                    return True
                    
                except sr.UnknownValueError:
                    self.add_debug("ERROR: Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    self.add_debug(f"ERROR: Could not request results from Google Speech Recognition service; {e}")
                    
        except sr.WaitTimeoutError:
            self.add_debug("ERROR: No speech detected within timeout period")
        except Exception as e:
            self.add_debug(f"ERROR: {e}")
            
        return False
    
    def update_display(self):
        """Update the display"""
        self.screen.fill((0, 0, 0))
        
        # Title
        title = self.font.render("Debug Translator - Italian to English", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # Instructions
        instructions = [
            "SPEAK ITALIAN INTO MICROPHONE TO TEST",
            "This will listen for 10 seconds and try to recognize Italian speech",
            "Check debug messages below for issues"
        ]
        
        y_offset = 50
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (255, 255, 0))
            self.screen.blit(text, (20, y_offset))
            y_offset += 20
        
        # Translated text
        y_offset += 20
        title = self.font.render("TRANSLATIONS:", True, (0, 255, 0))
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        if not self.translated_lines:
            text = self.font.render("No translations yet...", True, (128, 128, 128))
            self.screen.blit(text, (20, y_offset))
        else:
            for i, line in enumerate(self.translated_lines):
                text = self.font.render(line, True, (255, 255, 0))
                self.screen.blit(text, (20, y_offset + i * 25))
        
        # Debug messages
        y_offset = 300
        title = self.font.render("DEBUG MESSAGES:", True, (255, 0, 0))
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        for i, message in enumerate(self.debug_messages):
            color = (255, 100, 100) if "ERROR" in message else (100, 255, 100) if "SUCCESS" in message else (200, 200, 200)
            text = self.small_font.render(message, True, color)
            self.screen.blit(text, (20, y_offset + i * 18))
        
        # Controls
        controls = self.small_font.render("Press SPACE to test microphone | Q to quit", True, (128, 128, 255))
        self.screen.blit(controls, (20, 550))
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        self.add_debug("Debug translator started. Press SPACE to test microphone.")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.add_debug("Starting microphone test...")
                        # Run test in a way that doesn't block the UI
                        import threading
                        thread = threading.Thread(target=self.test_microphone)
                        thread.daemon = True
                        thread.start()
            
            self.update_display()
            pygame.time.delay(50)
        
        pygame.quit()

if __name__ == "__main__":
    debug = DebugTranslator()
    debug.run()