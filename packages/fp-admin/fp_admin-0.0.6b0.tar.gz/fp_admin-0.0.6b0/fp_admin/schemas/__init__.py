"""
Schemas package for fp-admin.

This package contains Pydantic schemas for request/response validation
and data serialization.
"""

from .base import BaseRequest, BaseResponse, BaseSchema

__all__ = ["BaseSchema", "BaseResponse", "BaseRequest"]
