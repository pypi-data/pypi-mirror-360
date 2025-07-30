"""
Base schemas for fp-admin.

This module provides base schema classes that other schemas should inherit from.
"""

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema class with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class BaseRequest(BaseSchema):
    """Base request schema."""


class BaseResponse(BaseSchema):
    """Base response schema."""


class PaginationParams(BaseRequest):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(
        default="asc", pattern="^(asc|desc)$", description="Sort order"
    )


class PaginatedResponse(BaseResponse):
    """Paginated response wrapper."""

    items: List[Any] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class ErrorResponse(BaseResponse):
    """Error response schema."""

    error: str = Field(description="Error message")
    status_code: int = Field(description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )


class SuccessResponse(BaseResponse):
    """Success response schema."""

    message: str = Field(description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Response timestamp"
    )


class HealthCheckResponse(BaseResponse):
    """Health check response schema."""

    status: str = Field(description="Service status")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Check timestamp"
    )
    version: str = Field(description="Application version")
    database: str = Field(description="Database status")
    cache: Optional[str] = Field(default=None, description="Cache status")


class SearchParams(BaseRequest):
    """Search parameters for search endpoints."""

    query: str = Field(description="Search query")
    fields: Optional[List[str]] = Field(default=None, description="Fields to search in")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional filters"
    )


class ExportParams(BaseRequest):
    """Export parameters for data export."""

    format: str = Field(description="Export format (csv, json, xlsx)")
    fields: Optional[List[str]] = Field(default=None, description="Fields to export")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Filters to apply"
    )


class ImportParams(BaseRequest):
    """Import parameters for data import."""

    format: str = Field(description="Import format (csv, json, xlsx)")
    update_existing: bool = Field(
        default=False, description="Whether to update existing records"
    )
    skip_errors: bool = Field(
        default=False, description="Whether to skip import errors"
    )


class AuditLogEntry(BaseResponse):
    """Audit log entry schema."""

    id: int = Field(description="Log entry ID")
    timestamp: datetime = Field(description="Event timestamp")
    user_id: Optional[int] = Field(
        default=None, description="User ID who performed the action"
    )
    action: str = Field(description="Action performed")
    resource_type: str = Field(description="Type of resource affected")
    resource_id: Optional[str] = Field(
        default=None, description="ID of resource affected"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional details"
    )


class SystemInfo(BaseResponse):
    """System information schema."""

    app_name: str = Field(description="Application name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment (development, production, etc.)")
    python_version: str = Field(description="Python version")
    database_url: str = Field(description="Database URL (masked)")
    installed_apps: List[str] = Field(description="List of installed apps")
    uptime: float = Field(description="Application uptime in seconds")


__all__ = [
    "BaseSchema",
    "BaseRequest",
    "BaseResponse",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "HealthCheckResponse",
    "SearchParams",
    "ExportParams",
    "ImportParams",
    "AuditLogEntry",
    "SystemInfo",
]
