"""
Field errors for fp-admin.

This module provides error handling for form fields.
"""

from pydantic import BaseModel


class FieldError(BaseModel):
    """Field validation error."""

    code: str
    message: str
