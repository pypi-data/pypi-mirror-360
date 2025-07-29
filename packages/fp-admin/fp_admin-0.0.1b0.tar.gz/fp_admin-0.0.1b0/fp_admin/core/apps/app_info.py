from typing import List, Dict, Any

from fp_admin.core.apps.app_config import apps_registry
from fp_admin.core.models.base import admin_model_registry


def app_info() -> List[Dict[str, Any]]:
    apps = []
    models = admin_model_registry.all() or []
    for app, config in apps_registry.all().items():
        app_models = [
            {"name": model.get("model_name"), "label": model.get("model_label")}
            for model in models
            if app == model.get("apps")
        ]
        apps.append({"name": app, "label": config.verbose_name, "models": app_models})
    return apps
