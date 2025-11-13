import queue
import sys

try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("sounddevice not available, trying pyaudio...")

if not SOUNDDEVICE_AVAILABLE:
    try:
        import pyaudio
        PYTHON_AUDIO_AVAILABLE = True
    except ImportError:
        PYTHON_AUDIO_AVAILABLE = False
        print("pyaudio not available either")

class AudioCapture:
    def __init__(self, rate=16000, chunk_size=1024, channels=1):
        self.rate = rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.audio_queue = queue.Queue()
        self.is_recording = False
        
        if SOUNDDEVICE_AVAILABLE:
            self.capture_method = "sounddevice"
            self.stream = None
        elif PYTHON_AUDIO_AVAILABLE:
            self.capture_method = "pyaudio"
            self.audio_interface = None
            self.audio_stream = None
        else:
            raise ImportError("No audio capture backend available")
            
        print(f"Using audio capture method: {self.capture_method}")
        
    def start_capture(self):
        """Start capturing audio from microphone"""
        self.is_recording = True
        
        if self.capture_method == "sounddevice":
            def audio_callback(indata, frames, time, status):
                """Callback for audio stream"""
                if self.is_recording:
                    # Convert numpy array to bytes
                    audio_bytes = (indata * 32767).astype(np.int16).tobytes()
                    self.audio_queue.put(audio_bytes)
            
            self.stream = sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=self.chunk_size,
                dtype='float32'
            )
            self.stream.start()
            
        elif self.capture_method == "pyaudio":
            self.audio_interface = pyaudio.PyAudio()
            self.audio_stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.audio_stream.start_stream()
        
        print("Audio capture started...")
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for pyaudio stream"""
        if self.is_recording:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def get_audio_data(self):
        """Get audio data from queue"""
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_capture(self):
        """Stop audio capture"""
        self.is_recording = False
        if self.capture_method == "sounddevice" and self.stream:
            self.stream.stop()
            self.stream.close()
        elif self.capture_method == "pyaudio":
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if self.audio_interface:
                self.audio_interface.terminate()
        print("Audio capture stopped.")