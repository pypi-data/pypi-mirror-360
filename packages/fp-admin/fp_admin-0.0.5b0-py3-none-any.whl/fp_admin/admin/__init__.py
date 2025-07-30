"""
Admin interface package for fp-admin.

This package contains all admin interface functionality including
views, forms, permissions, and widgets.
"""

# Import subpackages
from . import apps, fields, models, views

__all__ = [
    "apps",
    "models",
    "views",
    "fields",
]
