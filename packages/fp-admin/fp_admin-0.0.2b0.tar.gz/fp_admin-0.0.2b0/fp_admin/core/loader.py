import importlib
import os

from fp_admin import FpAdmin
from fp_admin.settings import settings


def load_app_routers(app: FpAdmin) -> None:
    """
    Auto-import and register routers from each apps.
    Looks for a `router` variable in `<apps>.routers`
    """
    for app_path in settings.INSTALLED_APPS:
        try:
            module = importlib.import_module(f"{app_path}.routers")
            router = getattr(module, "router", None)
            if router:
                router_path = f"{app.admin_path}/{app_path.split('.')[-1]}"
                app.include_router(router, prefix=router_path)
                print(f"✅ Registered router from {app_path}")
        except ModuleNotFoundError:
            print(f"⚠️  No router found in {app_path}")


def load_module(module_name: str) -> None:
    for app_path in settings.INSTALLED_APPS:
        try:
            print(f"{app_path}.{module_name}", os.path.realpath(__file__))
            importlib.import_module(f"{app_path}.{module_name}")
        except ModuleNotFoundError:
            pass


def load_modules(app: FpAdmin) -> None:
    for module_name in ("models", "apps", "admin", "views"):
        load_module(module_name)
    load_app_routers(app)
