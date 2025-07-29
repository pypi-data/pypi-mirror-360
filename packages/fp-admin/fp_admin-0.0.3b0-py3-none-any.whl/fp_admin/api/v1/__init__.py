from fastapi import APIRouter

from fp_admin.api.v1.apps_api import apps_router
from fp_admin.api.v1.views_api import views_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(apps_router, prefix="/apps", tags=["apps"])
v1_router.include_router(views_router, prefix="/views", tags=["views"])
