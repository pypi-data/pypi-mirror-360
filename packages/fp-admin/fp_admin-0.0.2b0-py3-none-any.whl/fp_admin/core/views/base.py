from abc import ABC, abstractmethod
from typing import List, Optional

from sqlmodel import SQLModel

from fp_admin.core.views.field_spec import FormField, FieldType
from fp_admin.core.views.types import BaseView


class BaseViewFactory(ABC):
    def __init__(self, model: type[SQLModel]):
        self.model = model

    @staticmethod
    def resolve_form_type(py_type: Optional[type]) -> FieldType:
        """Map Python types to field types."""
        mapping: dict[type, FieldType] = {
            str: "text",
            int: "number",
            float: "number",
            bool: "checkbox",
        }
        if py_type is None:
            return "text"
        return mapping.get(py_type, "text")

    def get_fields(self) -> List[FormField]:
        fields = []
        for fname, finfo in self.model.model_fields.items():
            fields.append(
                FormField(
                    name=fname,
                    label=finfo.title or fname.replace("_", " ").capitalize(),
                    field_type=self.resolve_form_type(finfo.annotation),
                )
            )
        return fields

    @abstractmethod
    def build_view(self) -> BaseView:
        pass
