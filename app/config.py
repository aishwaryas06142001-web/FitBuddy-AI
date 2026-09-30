from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    database_url: str = "sqlite:///./fitbuddy.db"
    gemini_api_key: str = ""
    workout_model: str = "gemini-3.8-flash"
    nutrition_model: str = "gemini-3.8-flash"
    mock_ai: bool = False
    admin_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
