# Configuration settings
class Config:
    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1
    
    # Language settings
    SOURCE_LANGUAGE = 'it'  # Italian
    TARGET_LANGUAGE = 'en'  # English
    
    # Recognition settings
    PHRASE_TIMEOUT = 3.0  # seconds
    
    # Display settings
    MAX_DISPLAY_LINES = 5
    FONT_SIZE = 24