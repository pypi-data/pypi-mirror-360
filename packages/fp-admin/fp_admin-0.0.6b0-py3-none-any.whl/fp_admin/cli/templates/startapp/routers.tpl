from fastapi import APIRouter

router = APIRouter(prefix="/{app_name}", tags=["{app_name}"])


# @router.get("/custom_router")
# def get_data():
#     return my_data
