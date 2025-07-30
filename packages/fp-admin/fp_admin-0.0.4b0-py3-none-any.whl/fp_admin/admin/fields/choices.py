"""
Field choices for fp-admin.

This module provides choice-related field components and field types.
"""

from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .base import FieldView


class FieldChoices(BaseModel):
    """Choice option for select fields."""

    title: str
    value: Union[str, bool, int]


class ChoicesField(FieldView):
    """Field with predefined choices."""

    field_type: Literal["select", "radio"] = "select"
    choices: List[FieldChoices] = Field(default_factory=list)

    @classmethod
    def choice_select_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "ChoicesField":
        """Create a select dropdown field with choices."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="select",
            choices=choices,
            **kwargs,
        )

    @classmethod
    def choice_radio_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "ChoicesField":
        """Create a radio button field with choices."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="radio",
            choices=choices,
            **kwargs,
        )

    @classmethod
    def choice_checkbox_group_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "ChoicesField":
        """Create a checkbox group field with choices."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="checkbox-group",
            choices=choices,
            **kwargs,
        )

    @classmethod
    def choice_autocomplete_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "ChoicesField":
        """Create an autocomplete field with choices."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="autocomplete",
            choices=choices,
            **kwargs,
        )


class MultiChoicesField(FieldView):
    """Field with predefined choices that allows multiple selection."""

    field_type: Literal["select"] = "select"
    choices: List[FieldChoices] = Field(default_factory=list)
    min_selections: Optional[int] = Field(
        default=None, description="Minimum number of selections required"
    )
    max_selections: Optional[int] = Field(
        default=None, description="Maximum number of selections allowed"
    )

    @classmethod
    def multi_choice_checkbox_group_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a checkbox group field for multiple selection."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="checkbox-group",
            choices=choices,
            **kwargs,
        )

    @classmethod
    def multi_choice_select_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a multi-select dropdown field."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="multi-select",
            choices=choices,
            **kwargs,
        )

    @classmethod
    def multi_choice_tags_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a tags field for multiple selection."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="tags",
            choices=choices,
            **kwargs,
        )

    @classmethod
    def multi_choice_chips_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a chips field for multiple selection."""
        return cls(
            name=name,
            title=title,
            field_type="select",
            widget="chips",
            choices=choices,
            **kwargs,
        )

    # Alias methods for backward compatibility and convenience
    @classmethod
    def multi_select_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a multi-select dropdown field (alias
        for multi_choice_select_field)."""
        return cls.multi_choice_select_field(
            name=name, title=title, choices=choices, **kwargs
        )

    @classmethod
    def tags_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a tags field for multiple selection (alias
        for multi_choice_tags_field)."""
        return cls.multi_choice_tags_field(
            name=name, title=title, choices=choices, **kwargs
        )

    @classmethod
    def chips_field(
        cls, name: str, title: str, choices: List[FieldChoices], **kwargs: Any
    ) -> "MultiChoicesField":
        """Create a chips field for multiple selection (alias
        for multi_choice_chips_field)."""
        return cls.multi_choice_chips_field(
            name=name, title=title, choices=choices, **kwargs
        )

    def validate_value(self, value: Any) -> List[str]:
        """Validate multi-choice field value and return error messages."""
        errors = []

        # Check required
        if self.required and (value is None or value == []):
            errors.append("This field is required")
            return errors

        # Skip validation for empty optional fields
        if not self.required and (value is None or value == []):
            return errors

        # Ensure value is a list
        if not isinstance(value, list):
            errors.append("Value must be a list of selections")
            return errors

        # Check minimum selections
        if self.min_selections and len(value) < self.min_selections:
            errors.append(f"Minimum {self.min_selections} selection(s) required")

        # Check maximum selections
        if self.max_selections and len(value) > self.max_selections:
            errors.append(f"Maximum {self.max_selections} selection(s) allowed")

        # Validate each selected value against choices
        valid_values = {choice.value for choice in self.choices}
        for selected_value in value:
            if selected_value not in valid_values:
                errors.append(f"Invalid selection: {selected_value}")

        return errors
