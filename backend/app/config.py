from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+psycopg://newsletters:newsletters_dev@localhost:5433/newsletters"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Admin seed
    admin_email: str = "admin@newsletter.local"
    admin_password: str = "changeme"

    # Brevo
    brevo_api_key: str = ""
    brevo_sender_email: str = "newsletter@yourdomain.com"
    brevo_sender_name: str = "My Newsletter"

    # Gemini
    gemini_api_key: str = ""

    # Gmail
    gmail_email: str = "you@gmail.com"
    gmail_app_password: str = ""
    gmail_label: str = "Newsletters"

    # App URLs
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
