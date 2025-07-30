"""
Custom exceptions for fp-admin framework.

This module defines all custom exceptions used throughout the application
to provide clear error handling and meaningful error messages.
"""

from typing import Any, Dict, Optional


class FastAPIAdminException(Exception):
    """Base exception for all fp-admin exceptions."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(FastAPIAdminException):
    """Raised when there's a configuration error."""


class DatabaseError(FastAPIAdminException):
    """Raised when there's a database-related error."""


class ModelError(FastAPIAdminException):
    """Raised when there's an error with model operations."""


class ViewError(FastAPIAdminException):
    """Raised when there's an error with admin views."""


class AuthenticationError(FastAPIAdminException):
    """Raised when there's an authentication error."""


class AuthorizationError(FastAPIAdminException):
    """Raised when there's an authorization error."""


class ValidationError(FastAPIAdminException):
    """Raised when data validation fails."""


class AppRegistryError(FastAPIAdminException):
    """Raised when there's an error with app registration."""


class TemplateError(FastAPIAdminException):
    """Raised when there's an error with template rendering."""


class MigrationError(FastAPIAdminException):
    """Raised when there's an error with database migrations."""


class CLIError(FastAPIAdminException):
    """Raised when there's an error with CLI operations."""


class APIError(FastAPIAdminException):
    """Raised when there's an error with API operations."""


class ServiceError(FastAPIAdminException):
    """Raised when there's an error with service operations."""


class CacheError(FastAPIAdminException):
    """Raised when there's an error with cache operations."""


class FileUploadError(FastAPIAdminException):
    """Raised when there's an error with file uploads."""


class ExportError(FastAPIAdminException):
    """Raised when there's an error with data export."""


class FpImportError(FastAPIAdminException):
    """Raised when there's an error with data import."""


# HTTP-specific exceptions
class HTTPError(FastAPIAdminException):
    """Base HTTP error exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code


class BadRequestError(HTTPError):
    """Raised for 400 Bad Request errors."""

    def __init__(
        self, message: str = "Bad Request", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 400, details)


class UnauthorizedError(HTTPError):
    """Raised for 401 Unauthorized errors."""

    def __init__(
        self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 401, details)


class ForbiddenError(HTTPError):
    """Raised for 403 Forbidden errors."""

    def __init__(
        self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 403, details)


class NotFoundError(HTTPError):
    """Raised for 404 Not Found errors."""

    def __init__(
        self, message: str = "Not Found", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 404, details)


class ConflictError(HTTPError):
    """Raised for 409 Conflict errors."""

    def __init__(
        self, message: str = "Conflict", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 409, details)


class UnprocessableEntityError(HTTPError):
    """Raised for 422 Unprocessable Entity errors."""

    def __init__(
        self,
        message: str = "Unprocessable Entity",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, 422, details)


__all__ = [
    "FastAPIAdminException",
    "ConfigurationError",
    "DatabaseError",
    "ModelError",
    "ViewError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "AppRegistryError",
    "TemplateError",
    "MigrationError",
    "CLIError",
    "APIError",
    "ServiceError",
    "CacheError",
    "FileUploadError",
    "ExportError",
    "FpImportError",
    "HTTPError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
]
