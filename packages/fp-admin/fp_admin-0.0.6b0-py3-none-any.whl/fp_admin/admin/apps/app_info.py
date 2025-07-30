from typing import Any, Dict, List

from fp_admin.admin.models import model_registry

from .app_config import apps_registry


def get_apps_info() -> List[Dict[str, Any]]:
    apps = []
    models = model_registry.all() or []
    for app, config in apps_registry.all().items():
        app_models = [
            {"name": model.get("model_name"), "label": model.get("model_label")}
            for model in models
            if app == model.get("apps")
        ]
        apps.append({"name": app, "label": config.verbose_name, "models": app_models})
    return apps
