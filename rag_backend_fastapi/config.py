"""Configuration settings for FastAPI backend"""
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "RAG Backend API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "chatbotgents-firebase-adminsdk-fbsvc-6af8f6e95e.json"
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    CHROMA_DB_PATH: Path = BASE_DIR / 'chroma_db'
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # LLM Configuration
    LLM_MODEL: str = "gemini-pro"
    GOOGLE_API_KEY: Optional[str] = None
    
    # RAG Configuration
    TOP_K_CHUNKS: int = 5
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=[".env", "../test.env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Resolve relative paths
        if not Path(self.FIREBASE_CREDENTIALS_PATH).is_absolute():
            self.FIREBASE_CREDENTIALS_PATH = str(self.BASE_DIR / self.FIREBASE_CREDENTIALS_PATH)
    
    def validate_required(self) -> None:
        """Validate required settings"""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        if not Path(self.FIREBASE_CREDENTIALS_PATH).exists():
            raise FileNotFoundError(
                f"Firebase credentials file not found: {self.FIREBASE_CREDENTIALS_PATH}"
            )


settings = Settings()

