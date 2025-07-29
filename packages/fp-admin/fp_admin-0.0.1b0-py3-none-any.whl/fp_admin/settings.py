from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    INSTALLED_APPS: List[str] = [
        "fp_admin.apps.auth",
    ]
    DATABASE_URL: str = "sqlite:///./models.sqlite3"
    DEBUG: bool = True


settings = Settings()
