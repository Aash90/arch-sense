from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./data/arch_sense_game.db"
    
    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-pro-preview"
    
    # Game
    difficulty_level: int = 1
    enable_hints: bool = True
    coaching_style: str = "aggressive"  # aggressive, balanced, gentle
    
    # CORS
    cors_origin: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
