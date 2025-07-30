from fastapi import APIRouter

from fp_admin.api.v1.apps_api import apps_api
from fp_admin.api.v1.views_api import views_api

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(apps_api, prefix="/apps", tags=["apps"])
v1_router.include_router(views_api, prefix="/views", tags=["views"])
