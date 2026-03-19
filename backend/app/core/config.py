import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Secure Smart Voting Verification System"
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production-please")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://voting_user:voting_pass@localhost:5432/voting_db",
    )

    # CORS & Host
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Face recognition thresholds
    FACE_MATCH_THRESHOLD: float = 0.6   # cosine distance; lower = stricter
    FACE_CONFIDENCE_MIN: float = 0.75   # minimum detection confidence

    # Ink detection thresholds (HSV color range for indelible blue/violet ink)
    INK_HUE_LOW: int = 100
    INK_HUE_HIGH: int = 160
    INK_SAT_LOW: int = 60
    INK_SAT_HIGH: int = 255
    INK_VAL_LOW: int = 30
    INK_VAL_HIGH: int = 200
    INK_PIXEL_RATIO_THRESHOLD: float = 0.002  # 0.2% of fingertip area must be inked

    # Fingerprint simulation (replace with real SDK values when hardware is attached)
    FP_MATCH_SCORE_THRESHOLD: int = 40   # 0-100 scale; ≥40 = match

    # Upload / temp storage
    UPLOAD_DIR: str = "/tmp/ssvvs_uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
