from abc import ABC, abstractmethod
from typing import List, Optional

from sqlmodel import SQLModel

from fp_admin.admin.fields import FieldType, FieldView
from fp_admin.admin.fields.utils import sqlmodel_to_fieldviews
from fp_admin.admin.views.types import BaseView


class BaseViewFactory(ABC):
    def __init__(self, model: type[SQLModel]):
        self.model = model

    @staticmethod
    def resolve_form_type(python_type: Optional[type]) -> FieldType:
        """Map Python types to field types."""
        mapping: dict[type, FieldType] = {
            str: "text",
            int: "number",
            float: "number",
            bool: "checkbox",
        }
        if python_type is None:
            return "text"
        return mapping.get(python_type, "text")

    def get_fields(self) -> List[FieldView]:
        return sqlmodel_to_fieldviews(self.model)

    @abstractmethod
    def build_view(self) -> BaseView:
        pass
