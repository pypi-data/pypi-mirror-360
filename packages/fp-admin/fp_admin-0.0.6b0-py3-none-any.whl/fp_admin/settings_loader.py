import importlib.util
from typing import Any

from pydantic_settings import BaseSettings

from fp_admin.global_settings import global_settings


class LazySettings:
    _settings_instance: BaseSettings | None = None

    def _load(self) -> BaseSettings:
        if self._settings_instance not in [None, global_settings]:
            return self._settings_instance

        # Try to import `settings` from the project using fp_admin
        if importlib.util.find_spec("settings") is not None:
            try:
                external_mod = importlib.import_module("settings")
                if hasattr(external_mod, "settings"):
                    self._settings_instance = external_mod.settings
                    return self._settings_instance
            except Exception as e:
                raise ImportError(
                    "Found `settings.py` but failed to load `settings` object."
                ) from e
        # Fallback to internal settings
        self._settings_instance = global_settings
        return self._settings_instance

    def __getattr__(self, item: str) -> Any:
        return getattr(self._load(), item)


settings = LazySettings()
