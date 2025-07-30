"""
Models package for fp-admin.

This package contains all data models and related functionality.
"""

from .base import AdminModel, AdminModelRegistry, model_registry

__all__ = ["AdminModelRegistry", "AdminModel", "model_registry"]
