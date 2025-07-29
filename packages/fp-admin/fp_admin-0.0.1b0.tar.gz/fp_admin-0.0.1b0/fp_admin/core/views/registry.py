from typing import Dict, List, Type
from sqlmodel import SQLModel
from fp_admin.core.views.types import BaseView


class ViewRegistry:
    _views: Dict[str, List[BaseView]] = {}

    @classmethod
    def register(cls, model: Type[SQLModel], view: BaseView) -> None:
        model_name = model.__name__
        if model_name not in cls._views:
            cls._views[model_name] = []
        cls._views[model_name].append(view)

    @classmethod
    def all(cls) -> Dict[str, List[BaseView]]:
        return cls._views

    @classmethod
    def get(cls, model_name: str) -> List[BaseView]:
        return cls._views.get(model_name, [])


view_registry = ViewRegistry()
