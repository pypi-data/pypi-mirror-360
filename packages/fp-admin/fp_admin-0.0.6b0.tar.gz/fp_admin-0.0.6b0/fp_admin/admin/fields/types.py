"""
Field types for fp-admin.

This module defines the supported field types for admin forms.
"""

from typing import Literal

FieldType = Literal[
    "text",
    "number",
    "date",
    "checkbox",
    "radio",
    "select",
    "textarea",
    "file",
    "relationship",
]
