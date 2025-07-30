"""
Field utilities for fp-admin.

This module provides utility functions for working with fields and SQLModel conversion.
"""

from typing import Any, List, Literal, cast, get_args, get_origin, get_type_hints

from sqlmodel import SQLModel

from .base import FieldView
from .types import FieldType
from .validation import FieldValidation


def sqlmodel_to_fieldviews(model: type[SQLModel]) -> List[FieldView]:
    """
    Convert a SQLModel class to a list of FieldView objects.

    Args:
        model: SQLModel class to convert

    Returns:
        List of FieldView objects representing the model's fields

    Example:
        >>> from sqlmodel import SQLModel, Field
        >>> from typing import Literal
        >>>
        >>> class User(SQLModel):
        ...     id: int = Field(primary_key=True)
        ...     name: str = Field(max_length=100)
        ...     status: Literal["active", "inactive"] = Field(default="active")
        >>>
        >>> fields = sqlmodel_to_fieldviews(User)
        >>> for field in fields:
        ...     print(f"{field.name}: {field.field_type}")
    """
    field_views = []
    type_hints = get_type_hints(model)

    for field_name, field_info in model.model_fields.items():
        # Skip internal SQLModel fields
        if field_name in ["__class__", "__dict__", "__weakref__"]:
            continue

        # Get field type and metadata
        field_type = type_hints.get(field_name, Any)

        # Skip primary key fields (fix: use getattr and check for True)
        if getattr(field_info, "primary_key", False) is True:
            continue

        # Determine field type based on Python type
        field_type_str = _get_field_type(field_type)

        # Create validation rules
        validation = _create_validation(field_info)

        # Create FieldView using appropriate class method
        field_view = _create_field_view(
            field_name=field_name,
            field_type=field_type_str,
            field_info=field_info,
            validation=validation,
            python_type=field_type,
        )

        field_views.append(field_view)

    return field_views


def _get_field_type(python_type: type) -> FieldType:
    """Convert Python type to FieldType."""
    origin = get_origin(python_type)

    if origin is not None:
        # Handle Optional[T], Union[T, None], etc.
        args = get_args(python_type)
        if type(None) in args:
            # Find the non-None type
            for arg in args:
                if arg is not type(None):
                    return _get_field_type(arg)

        # Handle Literal types
        if origin is Literal:
            return "select"

    # Type mapping for simple types
    type_mapping = {
        str: "text",
        int: "number",
        float: "number",
        bool: "checkbox",
        list: "select",  # Multi-select
    }

    # Check for list types with __origin__ attribute
    if (
        hasattr(python_type, "__origin__")
        and getattr(python_type, "__origin__") is list
    ):
        return "select"

    # Return mapped type or default to text
    return cast(FieldType, type_mapping.get(python_type, "text"))


def _get_literal_choices(python_type: type) -> List[dict[str, str]] | None:
    """Extract choices from Literal type."""
    origin = get_origin(python_type)

    if origin is Literal:
        args = get_args(python_type)
        choices = []
        for value in args:
            choices.append({"title": str(value).title(), "value": value})
        return choices

    return None


def _create_validation(field_info: Any) -> FieldValidation | None:
    """Create FieldValidation from SQLModel field info."""
    validation = FieldValidation()

    # Check for length constraints
    if hasattr(field_info, "max_length") and field_info.max_length:
        validation.max_length = field_info.max_length

    if hasattr(field_info, "min_length") and field_info.min_length:
        validation.min_length = field_info.min_length

    # Check for value constraints
    if hasattr(field_info, "gt") and field_info.gt is not None:
        validation.min_value = field_info.gt

    if hasattr(field_info, "gte") and field_info.gte is not None:
        validation.min_value = field_info.gte

    if hasattr(field_info, "lt") and field_info.lt is not None:
        validation.max_value = field_info.lt

    if hasattr(field_info, "lte") and field_info.lte is not None:
        validation.max_value = field_info.lte

    # Check for pattern validation (email, etc.)
    if hasattr(field_info, "pattern") and field_info.pattern:
        validation.pattern = field_info.pattern

    # Only return validation if we have some rules
    if any(
        [
            validation.min_length is not None,
            validation.max_length is not None,
            validation.min_value is not None,
            validation.max_value is not None,
            validation.pattern is not None,
        ]
    ):
        return validation

    return None


def _format_field_title(field_name: str) -> str:
    """Convert field name to human-readable title."""
    # Replace underscores with spaces and capitalize
    title = field_name.replace("_", " ").title()

    # Handle common abbreviations
    title = title.replace("Id", "ID")
    title = title.replace("Url", "URL")
    title = title.replace("Api", "API")

    return title


def _get_help_text(field_info: Any) -> str | None:
    """Extract help text from field info."""
    if hasattr(field_info, "description") and field_info.description:
        return cast(str, field_info.description)
    return None


def _get_placeholder(field_info: Any) -> str | None:
    """Generate placeholder text for field."""
    if hasattr(field_info, "placeholder") and field_info.placeholder:
        return cast(str, field_info.placeholder)

    # Generate placeholder based on field name
    field_name = getattr(field_info, "name", "")
    if field_name:
        return f"Enter {_format_field_title(field_name).lower()}"

    return None


def _create_field_view(
    field_name: str,
    field_type: FieldType,
    field_info: Any,
    validation: FieldValidation | None,
    python_type: type,
) -> FieldView:
    """Create FieldView using appropriate class method."""

    # Prepare kwargs for FieldView
    kwargs = {
        "required": field_info.is_required(),
        "default_value": field_info.default,
        "validation": validation,
        "help_text": _get_help_text(field_info),
        "placeholder": _get_placeholder(field_info),
    }

    # Handle Literal types with choices
    if field_type == "select":
        choices = _get_literal_choices(python_type)
        if choices:
            kwargs["options"] = choices

    # Field type to method mapping
    field_methods = {
        "text": FieldView.text_field,
        "number": FieldView.number_field,
        "checkbox": FieldView.checkbox_field,
        "date": FieldView.date_field,
        "textarea": FieldView.textarea_field,
        "file": FieldView.file_field,
        "select": FieldView.select_field,
    }

    # Get the appropriate method or default to text_field
    method = field_methods.get(field_type, FieldView.text_field)

    return method(name=field_name, title=_format_field_title(field_name), **kwargs)
