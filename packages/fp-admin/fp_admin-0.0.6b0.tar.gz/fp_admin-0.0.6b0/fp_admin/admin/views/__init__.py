"""
Admin views module for fp-admin.

This module provides the view system for the admin interface, including
view factories, builders, registry, and field specifications.
"""

# Import from base module
from .base import BaseViewFactory

# Import from builder module
from .builder import BaseViewBuilder

# Import from factories module
from .factories import FormViewFactory, ListViewFactory

# Import from registry module
from .registry import ViewRegistry, view_registry

# Import from types module
from .types import BaseView, FormView, ListView

__all__ = [
    # Base classes
    "BaseViewFactory",
    "BaseViewBuilder",
    # View types
    "BaseView",
    "FormView",
    "ListView",
    # Registry
    "ViewRegistry",
    "view_registry",
    # Factories
    "FormViewFactory",
    "ListViewFactory",
]
