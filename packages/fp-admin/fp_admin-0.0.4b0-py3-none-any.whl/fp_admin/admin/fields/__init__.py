"""
Field specifications for fp-admin.

This package provides field types, validation rules, and field specifications
used throughout the admin interface for form generation.
"""

from .base import FieldView
from .choices import ChoicesField, FieldChoices, MultiChoicesField
from .errors import FieldError
from .relationships import RelationshipField
from .types import FieldType
from .validation import FieldValidation
from .widgets import DEFAULT_WIDGETS, WidgetType

__all__ = [
    # Field types
    "FieldType",
    # Validation
    "FieldValidation",
    # Field components
    "FieldChoices",
    "FieldError",
    # Field classes
    "FieldView",
    "ChoicesField",
    "MultiChoicesField",
    "RelationshipField",
    # Widget types
    "WidgetType",
    "DEFAULT_WIDGETS",
]
