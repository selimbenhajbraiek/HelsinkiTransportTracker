import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "Helsinki Transport Tracker"
    PROJECT_DESCRIPTION: str = "Real-time tracking and statistics for Helsinki public transport"
    PROJECT_VERSION: str = "1.0.0"
    
    # API URLs and keys
    DIGITRANSIT_API_URL: str = os.getenv("DIGITRANSIT_API_URL", "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql")
    DIGITRANSIT_API_KEY: str = os.getenv("DIGITRANSIT_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/helsinki_transport")
    
    # Grafana settings
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "http://localhost:3000")
    GRAFANA_API_KEY: str = os.getenv("GRAFANA_API_KEY", "")
    
    # Data collection settings
    VEHICLE_COLLECTION_INTERVAL: int = int(os.getenv("VEHICLE_COLLECTION_INTERVAL", "60"))  # seconds
    CLEANUP_INTERVAL: int = int(os.getenv("CLEANUP_INTERVAL", "86400"))  # seconds (1 day)
    DATA_RETENTION_DAYS: int = int(os.getenv("DATA_RETENTION_DAYS", "30"))  # days

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()