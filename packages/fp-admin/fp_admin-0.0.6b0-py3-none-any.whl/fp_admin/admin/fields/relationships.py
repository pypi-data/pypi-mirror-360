"""
Relationship fields for fp-admin.

This module provides relationship field types for model associations.
"""

from typing import Any, Literal

from .base import FieldView


class RelationshipField(FieldView):
    """Field for relationship selection."""

    field_type: Literal["relationship"] = "relationship"
    model: str
    id_field: str = "id"
    title_field: str = "title"

    @classmethod
    def relationship_field(
        cls, name: str, title: str, model: str, **kwargs: Any
    ) -> "RelationshipField":
        """Create a relationship field."""
        return cls(
            name=name, title=title, field_type="relationship", model=model, **kwargs
        )
