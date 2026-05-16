from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ALERT_API_URL: str = "http://example.com/api/alert_endpoint"
    PORT: int = 8000
    
    # Storage settings
    FRAME_DIR: Path = Path("frames")
    OUTPUT_DIR: Path = Path("outputs")
    DB_PATH: Path = Path("camera_events.db")
    WEIGHTS_PATH: Path = Path("weights/rf-detr-medium.pth")
    
    # Business logic settings
    PHONE_USAGE_THRESHOLD_SECONDS: int = 300  # 5 minutes

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
settings.FRAME_DIR.mkdir(exist_ok=True)
settings.OUTPUT_DIR.mkdir(exist_ok=True)
