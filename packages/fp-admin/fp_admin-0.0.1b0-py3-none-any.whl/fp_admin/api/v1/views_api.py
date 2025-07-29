from typing import Any

from fastapi import APIRouter

from fp_admin.core.views.registry import view_registry

views_router = APIRouter()


@views_router.get("/")
def list_registered_views() -> Any:
    return view_registry.all()


@views_router.get("/{model_name}")
async def get_views_for_model(model_name: str) -> Any:
    return view_registry.get(model_name)
