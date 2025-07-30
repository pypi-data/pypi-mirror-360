"""
Module loader for fp-admin.

This module handles automatic discovery and loading of apps, models, views, and routers.
"""

import importlib
import logging
import sys
from typing import TYPE_CHECKING

from fp_admin.settings_loader import settings

if TYPE_CHECKING:
    from fp_admin import FastAPIAdmin

logger = logging.getLogger(__name__)


def load_app_routers(app: "FastAPIAdmin") -> None:
    """
    Auto-import and register routers from each app.

    Looks for a `router` variable in `<app>.routers`

    Args:
        app: The FastAPI Admin application instance
    """
    for app_path in settings.INSTALLED_APPS:
        try:
            module = importlib.import_module(f"{app_path}.routers")
            router = getattr(module, "router", None)
            if router:
                router_path = f"{app.admin_path}/{app_path.split('.')[-1]}"
                app.include_router(router, prefix=router_path)
                logger.info("✅ Registered router from %s", app_path)
            else:
                logger.debug("⚠️  No router found in %s", app_path)
        except ModuleNotFoundError:
            logger.debug("⚠️  No routers module found in %s", app_path)
        except (ImportError, AttributeError) as e:
            logger.error("❌ Error loading router from %s: %s", app_path, e)


def load_module(module_name: str) -> None:
    """
    Load a specific module from all installed apps.

    Args:
        module_name: Name of the module to load (e.g., 'models', 'views')
    """
    for app_path in settings.INSTALLED_APPS:
        try:
            importlib.import_module(f"{app_path}.{module_name}")
            logger.debug("✅ Loaded %s from %s", module_name, app_path)
        except ModuleNotFoundError:
            logger.debug("⚠️  No %s module found in %s", module_name, app_path)
        except ImportError as e:
            logger.error("❌ Error loading %s from %s: %s", module_name, app_path, e)


def load_modules(app: "FastAPIAdmin") -> None:
    """
    Load all required modules from installed apps.

    Args:
        app: The FastAPI Admin application instance
    """
    logger.info("🔄 Loading modules from installed apps...")

    # Load core modules in order
    module_order = ["models", "admin", "views", "apps"]

    for module_name in module_order:
        load_module(module_name)

    # Load app routers
    load_app_routers(app)

    logger.info("✅ All modules loaded successfully")


def reload_app(app_path: str) -> None:
    """
    Reload a specific app and its modules.

    Args:
        app_path: Path to the app to reload
    """
    try:
        # Reload the app module
        if app_path in sys.modules:
            importlib.reload(sys.modules[app_path])

        # Reload specific modules
        for module_name in ["models", "admin", "views", "apps"]:
            module_full_path = f"{app_path}.{module_name}"
            if module_full_path in sys.modules:
                importlib.reload(sys.modules[module_full_path])

        logger.info("✅ Reloaded app: %s", app_path)
    except (ImportError, AttributeError) as e:
        logger.error("❌ Error reloading app %s: %s", app_path, e)


def get_loaded_apps() -> list[str]:
    """
    Get list of successfully loaded apps.

    Returns:
        List of app paths that were successfully loaded
    """
    loaded_apps = []

    for app_path in settings.INSTALLED_APPS:
        try:
            importlib.import_module(app_path)
            loaded_apps.append(app_path)
        except (ImportError, ModuleNotFoundError):
            pass

    return loaded_apps
