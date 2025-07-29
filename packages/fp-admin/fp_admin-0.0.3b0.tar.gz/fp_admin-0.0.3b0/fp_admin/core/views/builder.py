from typing import List, Type, Literal, Optional

from sqlmodel import SQLModel
from fp_admin.core.views.registry import view_registry
from fp_admin.core.views.types import BaseView, FormView, ListView
from fp_admin.core.views.factories import FormViewFactory, ListViewFactory
from fp_admin.core.views.field_spec import FormField


class BaseViewBuilder:
    name: str
    model: Type[SQLModel]
    view_type: Literal["form", "list"]
    fields: List[FormField]
    default_form_id: Optional[str] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        # If any key attribute is missing, call build()
        if not all(
            [
                getattr(cls, "name", None),
                getattr(cls, "fields", None),
            ]
        ):
            instance = cls()
            view = instance.build()
        else:
            # Construct the view from class attributes
            view = cls.create_from_attrs()

        view_registry.register(cls.model, view)

    def build(self) -> BaseView:
        if self.view_type == "form":
            return FormViewFactory(self.model).build_view()
        elif self.view_type == "list":
            return ListViewFactory(self.model).build_view()
        else:
            raise ValueError(f"Unknown view type: {self.view_type}")

    @classmethod
    def create_from_attrs(cls) -> BaseView:
        if cls.view_type == "form":
            return FormView(
                name=cls.name,
                view_type="form",
                model=cls.model.__name__,
                fields=cls.fields or [],
            )
        elif cls.view_type == "list":
            return ListView(
                name=cls.name,
                view_type="list",
                model=cls.model.__name__,
                default_form_id=cls.default_form_id or f"{cls.model.__name__}Form",
                fields=cls.fields or [],
            )
        else:
            raise ValueError(f"Unknown view type: {cls.view_type}")
