from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/users")
def list_users() -> List[Dict[str, Any]]:
    return [{"id": 1, "username": "models"}]
