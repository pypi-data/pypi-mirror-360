"""
Application constants for fp-admin.

This module defines all constants used throughout the application
to ensure consistency and maintainability.
"""

from enum import Enum
from typing import List

# Application constants
APP_NAME = "fp-admin"
APP_DESCRIPTION = "FastAPI Admin Framework"

# Default paths
DEFAULT_ADMIN_PATH = "/admin"
DEFAULT_API_PREFIX = "/api/v1"
DEFAULT_UPLOAD_DIR = "./data/uploads"
DEFAULT_LOG_DIR = "./logs"

# Database constants
DEFAULT_DATABASE_URL = "sqlite:///./models.sqlite3"
DEFAULT_TEST_DATABASE_URL = "sqlite:///./test.db"

# Security constants
DEFAULT_SECRET_KEY = "your-secret-key-change-in-production"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7


# Pagination constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Cache constants
DEFAULT_CACHE_TTL = 3600  # 1 hour
DEFAULT_CACHE_PREFIX = "fp_admin"

# Logging constants
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Field types for admin forms
class FieldType(str, Enum):
    """Available field types for admin forms."""

    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    URL = "url"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    MULTISELECT = "multiselect"
    TEXTAREA = "textarea"
    RICHTEXT = "richtext"
    FILE = "file"
    IMAGE = "image"
    JSON = "json"
    COLOR = "color"
    RANGE = "range"
    TEL = "tel"
    SEARCH = "search"
    HIDDEN = "hidden"


# View types
class ViewType(str, Enum):
    """Available view types for admin interface."""

    FORM = "form"
    LIST = "list"
    DETAIL = "detail"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# Permission constants
class PermissionType(str, Enum):
    """Available permission types."""

    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"


# HTTP status codes
class HTTPStatus:
    """HTTP status codes used in the application."""

    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


# Environment constants
class Environment(str, Enum):
    """Application environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


# Database engines
class DatabaseEngine(str, Enum):
    """Supported database engines."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"


# Cache backends
class CacheBackend(str, Enum):
    """Supported cache backends."""

    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"


# Default middleware
DEFAULT_MIDDLEWARE: List[str] = [
    "fp_admin.api.middleware.cors",
    "fp_admin.api.middleware.logging",
    "fp_admin.api.middleware.security",
]


# API response formats
class ResponseFormat(str, Enum):
    """API response formats."""

    JSON = "json"
    XML = "xml"
    YAML = "yaml"


# Validation patterns
class ValidationPattern:
    """Common validation patterns."""

    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    URL = (
        r"^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*"
        r"(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$"
    )
    PHONE = r"^\+?[\d\s\-\(\)]+$"
    PASSWORD = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"


# Error messages
class ErrorMessages:
    """Common error messages."""

    REQUIRED_FIELD = "This field is required."
    INVALID_EMAIL = "Please enter a valid email address."
    INVALID_URL = "Please enter a valid URL."
    INVALID_PHONE = "Please enter a valid phone number."
    WEAK_PASSWORD = (
        "Password must be at least 8 characters long and contain uppercase, "
        "lowercase, number, and special character."
    )
    FILE_TOO_LARGE = "File size exceeds maximum allowed size."
    INVALID_FILE_TYPE = "File type not allowed."
    NOT_FOUND = "The requested resource was not found."
    UNAUTHORIZED = "You are not authorized to perform this action."
    FORBIDDEN = "Access denied."
    VALIDATION_ERROR = "Validation error occurred."
    INTERNAL_ERROR = "An internal error occurred."


# Success messages
class SuccessMessages:
    """Common success messages."""

    CREATED = "Resource created successfully."
    UPDATED = "Resource updated successfully."
    DELETED = "Resource deleted successfully."
    EXPORTED = "Data exported successfully."
    IMPORTED = "Data imported successfully."
    LOGGED_IN = "Logged in successfully."
    LOGGED_OUT = "Logged out successfully."
    PASSWORD_CHANGED = "Password changed successfully."


# CLI command names
class CLICommands:
    """CLI command names."""

    VERSION = "version"
    STARTPROJECT = "startproject"
    STARTAPP = "startapp"
    MAKEMIGRATIONS = "make-migrations"
    MIGRATE = "migrate"
    CREATESUPERUSER = "createsuperuser"
    SHELL = "shell"
    CHECK = "check"


# Export all constants
__all__ = [
    # Application
    "APP_NAME",
    "APP_DESCRIPTION",
    # Paths
    "DEFAULT_ADMIN_PATH",
    "DEFAULT_API_PREFIX",
    "DEFAULT_UPLOAD_DIR",
    "DEFAULT_LOG_DIR",
    # Database
    "DEFAULT_DATABASE_URL",
    "DEFAULT_TEST_DATABASE_URL",
    # Security
    "DEFAULT_SECRET_KEY",
    "DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS",
    # Pagination
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MIN_PAGE_SIZE",
    # Cache
    "DEFAULT_CACHE_TTL",
    "DEFAULT_CACHE_PREFIX",
    # Logging
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_DATE_FORMAT",
    # Enums
    "FieldType",
    "ViewType",
    "PermissionType",
    "HTTPStatus",
    "Environment",
    "DatabaseEngine",
    "CacheBackend",
    "ResponseFormat",
    # Lists
    "DEFAULT_MIDDLEWARE",
    # Classes
    "ValidationPattern",
    "ErrorMessages",
    "SuccessMessages",
    "CLICommands",
]
