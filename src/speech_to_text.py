import speech_recognition as sr
import io

class SpeechToText:
    def __init__(self, language='it-IT'):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.audio_data_buffer = bytearray()
        
    def add_audio_data(self, audio_data):
        """Add audio data to buffer"""
        self.audio_data_buffer.extend(audio_data)
        
    def recognize_speech(self):
        """Convert audio buffer to text"""
        if len(self.audio_data_buffer) < 16000 * 2:  # Minimum 1 second of audio
            return None
            
        try:
            # Convert bytearray to AudioData
            audio_data = sr.AudioData(
                bytes(self.audio_data_buffer), 
                16000, 
                2
            )
            
            # Clear buffer after processing
            self.audio_data_buffer.clear()
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(
                audio_data, 
                language=self.language
            )
            return text
            
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None