"""
Base field classes for fp-admin.

This module provides the base field class and factory methods for creating form fields.
"""

import re
from typing import Any, List, Optional, TypedDict

from pydantic import BaseModel

from .errors import FieldError
from .types import FieldType
from .validation import FieldValidation
from .widgets import DEFAULT_WIDGETS, WidgetType


class FieldViewKwargs(TypedDict, total=False):
    """Keyword arguments for FieldView initialization."""

    help_text: Optional[str]
    widget: Optional[WidgetType]
    required: bool
    readonly: bool
    disabled: bool
    placeholder: Optional[str]
    default_value: Optional[Any]
    options: Optional[List[dict[str, str]]]
    error: Optional[FieldError]
    validation: Optional[FieldValidation]
    is_primary_key: bool


def get_default_widget(field_type: FieldType) -> WidgetType:
    """Get the default widget for a field type with proper typing."""
    return DEFAULT_WIDGETS.get(field_type, "text")


class FieldView(BaseModel):
    """Form field specification for admin interface."""

    name: str
    title: Optional[str] = None
    help_text: Optional[str] = None
    field_type: FieldType
    widget: Optional[WidgetType] = None
    required: bool = False
    readonly: bool = False
    disabled: bool = False
    placeholder: Optional[str] = None
    default_value: Optional[Any] = None
    options: Optional[List[dict[str, str]]] = None
    error: Optional[FieldError] = None
    validation: Optional[FieldValidation] = None
    is_primary_key: bool = False

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize FieldView with proper typing.

        Args:
            **kwargs: Any valid field attributes for FieldView
        """
        super().__init__(**kwargs)
        # Set default widget if not provided
        if self.widget is None:
            self.widget = get_default_widget(self.field_type)

    @classmethod
    def text_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a text input field."""
        return cls(name=name, title=title, field_type="text", **kwargs)

    @classmethod
    def email_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create an email input field."""
        validation = FieldValidation(
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        return cls(
            name=name, title=title, field_type="text", validation=validation, **kwargs
        )

    @classmethod
    def password_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a password input field."""
        return cls(name=name, title=title, field_type="text", **kwargs)

    @classmethod
    def number_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a number input field."""
        return cls(name=name, title=title, field_type="number", **kwargs)

    @classmethod
    def date_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a date input field."""
        return cls(name=name, title=title, field_type="date", **kwargs)

    @classmethod
    def checkbox_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a checkbox field."""
        return cls(name=name, title=title, field_type="checkbox", **kwargs)

    @classmethod
    def textarea_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a textarea field."""
        return cls(name=name, title=title, field_type="textarea", **kwargs)

    @classmethod
    def file_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a file upload field."""
        return cls(name=name, title=title, field_type="file", **kwargs)

    # Widget-specific factory methods
    @classmethod
    def select_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a select dropdown field."""
        return cls(
            name=name, title=title, field_type="select", widget="select", **kwargs
        )

    @classmethod
    def radio_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a radio button field."""
        return cls(
            name=name, title=title, field_type="select", widget="radio", **kwargs
        )

    @classmethod
    def checkbox_group_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a checkbox group field."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="checkbox-group",
            **kwargs,
        )

    @classmethod
    def autocomplete_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create an autocomplete field."""
        return cls(
            name=name, title=title, field_type="select", widget="autocomplete", **kwargs
        )

    @classmethod
    def toggle_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a toggle switch field."""
        return cls(
            name=name, title=title, field_type="checkbox", widget="toggle", **kwargs
        )

    @classmethod
    def switch_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a switch field."""
        return cls(
            name=name, title=title, field_type="checkbox", widget="switch", **kwargs
        )

    @classmethod
    def range_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a range slider field."""
        return cls(
            name=name, title=title, field_type="number", widget="range", **kwargs
        )

    @classmethod
    def slider_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a slider field."""
        return cls(
            name=name, title=title, field_type="number", widget="slider", **kwargs
        )

    @classmethod
    def richtext_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a rich text editor field."""
        return cls(
            name=name, title=title, field_type="textarea", widget="richtext", **kwargs
        )

    @classmethod
    def markdown_field(cls, name: str, title: str, **kwargs: Any) -> "FieldView":
        """Create a markdown editor field."""
        return cls(
            name=name, title=title, field_type="textarea", widget="markdown", **kwargs
        )

    def validate_value(self, value: Any) -> List[str]:
        """Validate field value and return error messages."""
        errors = []

        # Check required
        if self.required and (value is None or value == ""):
            errors.append("This field is required")
            return errors

        # Skip validation for empty optional fields
        if not self.required and (value is None or value == ""):
            return errors

        # Apply validation rules
        if self.validation:
            # Length validation
            if (
                self.validation.min_length
                and len(str(value)) < self.validation.min_length
            ):
                errors.append(
                    f"Minimum length is {self.validation.min_length} characters"
                )

            if (
                self.validation.max_length
                and len(str(value)) > self.validation.max_length
            ):
                errors.append(
                    f"Maximum length is {self.validation.max_length} characters"
                )

            # Value validation
            if (
                self.validation.min_value is not None
                and value < self.validation.min_value
            ):
                errors.append(f"Minimum value is {self.validation.min_value}")

            if (
                self.validation.max_value is not None
                and value > self.validation.max_value
            ):
                errors.append(f"Maximum value is {self.validation.max_value}")

            # Pattern validation
            if self.validation.pattern:

                if not re.match(self.validation.pattern, str(value)):
                    errors.append("Invalid format")

        return errors
