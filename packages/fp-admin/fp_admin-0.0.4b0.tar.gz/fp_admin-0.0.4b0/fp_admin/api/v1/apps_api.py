from typing import Any

from fastapi import APIRouter

from fp_admin.admin.apps import get_apps_info

apps_api = APIRouter()


@apps_api.get("/")
def list_apps() -> Any:
    return get_apps_info()
