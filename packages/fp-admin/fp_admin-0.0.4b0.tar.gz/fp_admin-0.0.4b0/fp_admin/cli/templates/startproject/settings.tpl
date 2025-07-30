import os

from pydantic import Field

from pydantic_settings import BaseSettings
from typing import List, Optional

from fp_admin.constants import DEFAULT_LOG_FORMAT


class Settings(BaseSettings):
    INSTALLED_APPS: List[str] = [
        "fp_admin.apps.auth",
    ]
    DATABASE_URL: str = "sqlite:///./models.sqlite3"
    DEBUG: bool = True
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    # Admin settings
    ADMIN_PATH: str = Field(
        default="/admin",
        description="Admin interface URL path"
    )
    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration time"
    )
    LOG_FORMAT: str = Field(
        default=DEFAULT_LOG_FORMAT,
        description="Log message format"
    )

    # Caching settings
    CACHE_URL: Optional[str] = Field(
        default=None,
        description="Cache backend URL (Redis, etc.)"
    )
    CACHE_TTL: int = Field(
        default=3600,
        description="Default cache TTL in seconds"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    RELOAD_ON_CHANGE: bool = Field(
        default=False,
        description="Auto-reload on file changes"
    )

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return os.getenv("TESTING", "false").lower() == "true"




# Environment-specific settings
class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    RELOAD_ON_CHANGE: bool = False


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "ERROR"


def get_environment_settings() -> Settings:
    """Get environment-specific settings."""
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

settings = get_environment_settings()
