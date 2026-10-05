import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "GrowthOS V2 API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database configuration (Supabase PostgreSQL / SQLite fallback)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./growthos.db"
    )
    
    # OpenRouter API Key for free LLM models
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    class Config:
        case_sensitive = True

settings = Settings()
