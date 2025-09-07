"""
Configuration settings for the AI Meeting Summarizer
"""

import os
from typing import Optional

class Settings:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # AI Model Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
    SUMMARIZER_MODEL: str = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
    NER_MODEL: str = os.getenv("NER_MODEL", "dbmdz/bert-large-cased-finetuned-conll03-english")
    
    # OpenAI Configuration (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Google Speech-to-Text Configuration (optional)
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100MB default
    ALLOWED_AUDIO_FORMATS: list = ["wav", "mp3", "mp4", "m4a", "flac", "ogg"]
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    
    # Processing Configuration
    MAX_TRANSCRIPT_LENGTH: int = int(os.getenv("MAX_TRANSCRIPT_LENGTH", "50000"))
    DEFAULT_SUMMARY_LENGTH: int = int(os.getenv("DEFAULT_SUMMARY_LENGTH", "150"))
    MIN_SUMMARY_LENGTH: int = int(os.getenv("MIN_SUMMARY_LENGTH", "50"))
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    
    def __init__(self):
        # Create upload directory if it doesn't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

# Global settings instance
settings = Settings()