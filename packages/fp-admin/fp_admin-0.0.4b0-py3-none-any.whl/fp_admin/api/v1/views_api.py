from typing import Dict, List

from fastapi import APIRouter

from fp_admin.admin.views import BaseView, view_registry

views_api = APIRouter()


@views_api.get(
    "/", response_model=Dict[str, List[BaseView]], response_model_exclude_none=True
)
def get_views() -> Dict[str, List[BaseView]]:
    return view_registry.all()


@views_api.get(
    "/{model_name}", response_model=List[BaseView], response_model_exclude_none=True
)
async def get_model_views(model_name: str) -> List[BaseView]:
    return view_registry.get(model_name)
