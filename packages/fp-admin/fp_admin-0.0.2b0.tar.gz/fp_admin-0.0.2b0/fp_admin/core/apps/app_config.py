from typing import Dict


class AppConfig:
    name: str
    verbose_name: str

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if not hasattr(cls, "name"):
            raise ValueError(f"{cls.__name__} must define a `name`")
        apps_registry.register(cls())


class AppRegistry:
    _apps: Dict[str, AppConfig] = {}

    @classmethod
    def register(cls, config: AppConfig) -> None:
        cls._apps[config.name] = config

    @classmethod
    def all(cls) -> Dict[str, AppConfig]:
        return cls._apps

    @classmethod
    def get(cls, name: str) -> AppConfig:
        return cls._apps[name]


apps_registry = AppRegistry()
