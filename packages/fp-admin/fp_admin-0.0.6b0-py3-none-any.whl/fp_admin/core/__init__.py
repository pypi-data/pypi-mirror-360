"""
Core package for fp-admin.

This package contains core functionality including database management,
module loading, and utility functions.
"""

from .database import check_database_health, db_manager, get_db
from .loader import (
    get_loaded_apps,
    load_app_routers,
    load_module,
    load_modules,
    reload_app,
)

__all__ = [
    # Database
    "db_manager",
    "get_db",
    "check_database_health",
    "load_modules",
    "load_app_routers",
    "get_loaded_apps",
    # Loader
    "load_app_routers",
    "load_module",
    "load_modules",
    "reload_app",
    "get_loaded_apps",
]
