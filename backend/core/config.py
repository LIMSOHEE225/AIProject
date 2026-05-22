import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "DearZit"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    TRIPO_API_KEY: str = os.getenv("TRIPO_API_KEY", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        case_sensitive = True

settings = Settings()
