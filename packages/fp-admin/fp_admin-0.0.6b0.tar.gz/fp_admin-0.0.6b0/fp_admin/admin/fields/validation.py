"""
Field validation for fp-admin.

This module provides validation rules and validation logic for form fields.
"""

from typing import Optional, Union

from pydantic import BaseModel


class FieldValidation(BaseModel):
    """Basic field validation rules."""

    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None  # Regex pattern for validation
