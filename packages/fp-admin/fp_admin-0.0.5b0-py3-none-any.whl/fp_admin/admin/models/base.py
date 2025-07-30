from typing import Any, Dict, List, Optional, Type

from sqlmodel import SQLModel


class AdminModelRegistry:
    _registry: List[Dict[str, Any]] = []

    @classmethod
    def register(cls, config: "AdminModel") -> None:
        cls._registry.append(
            {
                "model": config.model,
                "model_name": config.model.__name__,
                "model_label": config.label,
                "apps": config.model.__module__.split(".")[-2],
            }
        )

    @classmethod
    def all(cls) -> List[Dict[str, Any]]:
        return cls._registry


model_registry = AdminModelRegistry()


class AdminModel:
    model: Type[SQLModel]
    label: Optional[str] = None

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "model"):
            model_registry.register(cls())
