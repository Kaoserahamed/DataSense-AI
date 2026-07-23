from pydantic_settings import BaseSettings
from typing import Optional


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
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
