from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DataSense AI"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./datasense_ai.db"
    
    # OpenAI
    OPENAI_API_KEY: str = "sk-test-key"
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    
    # CORS — comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    def get_allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
