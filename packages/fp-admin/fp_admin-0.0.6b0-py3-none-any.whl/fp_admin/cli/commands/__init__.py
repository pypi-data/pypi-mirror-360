"""
CLI commands package for fp-admin.

This package contains all CLI command implementations organized by functionality.
"""

from .database import database_app
from .project import project_app
from .system import system_app
from .user import user_app

__all__ = [
    "project_app",
    "database_app",
    "user_app",
    "system_app",
]
