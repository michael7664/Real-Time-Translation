from googletrans import Translator
import logging

# Configure logging to reduce verbosity
logging.getLogger('googletrans').setLevel(logging.ERROR)

class TextTranslator:
    def __init__(self, src_lang='it', dest_lang='en'):
        self.translator = Translator()
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        
    def translate_text(self, text):
        """Translate text from source to destination language"""
        try:
            if not text or len(text.strip()) == 0:
                return ""
                
            translation = self.translator.translate(
                text, 
                src=self.src_lang, 
                dest=self.dest_lang
            )
            return translation.text
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[Translation failed] {text}"