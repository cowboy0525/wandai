from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Database Configuration
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # File Upload Configuration
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    
    # API Configuration
    api_title: str = "Wand AI - Multi-Agent Knowledge Base"
    api_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Configuration
    allowed_origins: list = ["*"]  # In production, restrict this
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate(self):
        """Validate required settings"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.chroma_db_path, exist_ok=True)

# Global settings instance
settings = Settings()
settings.validate()
