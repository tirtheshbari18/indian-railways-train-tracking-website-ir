import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "RailTrack India - IR Passenger Information System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # Default to sqlite local database for instant zero-configuration development,
    # or override with DATABASE_URL (e.g. postgresql://postgres:postgres@localhost:5432/railtracker)
    raw_db_url = os.getenv("DATABASE_URL", "")
    if not raw_db_url:
        if os.getenv("VERCEL"):
            raw_db_url = "sqlite:////tmp/railtracker.db"
        else:
            raw_db_url = "sqlite:///./railtracker.db"

    # Normalize postgres:// to postgresql:// for SQLAlchemy 2.0 compatibility
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    DATABASE_URL: str = raw_db_url
    
    # JWT & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "railway-super-secret-key-cris-railtel-2026-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Default Admin Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@railtrack.gov.in")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "RailAdmin@2026")
    
    # Tracking Provider Mode: 'mock' (synthetic demo feed), 'api' (external IR API), or 'null' (unavailable)
    TRACKING_PROVIDER: str = os.getenv("TRACKING_PROVIDER", "mock")
    EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL", "")
    EXTERNAL_API_KEY: str = os.getenv("EXTERNAL_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

settings = Settings()
