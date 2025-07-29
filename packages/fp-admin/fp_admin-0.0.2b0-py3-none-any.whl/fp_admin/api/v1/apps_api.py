from typing import Any

from fastapi import APIRouter

from fp_admin.core.apps.app_info import app_info

apps_router = APIRouter()


@apps_router.get("/")
def list_apps() -> Any:
    return app_info()
