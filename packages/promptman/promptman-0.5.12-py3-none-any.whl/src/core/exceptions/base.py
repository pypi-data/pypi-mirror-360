"""
Base exception classes for the AI Prompt Manager application.

This module defines the exception hierarchy used throughout the application
to provide consistent error handling and better debugging capabilities.
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """
    Base exception for all application errors.

    This serves as the root of the exception hierarchy and provides
    common functionality for all application-specific exceptions.
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base exception.

        Args:
            message: Human-readable error message
            code: Optional error code for programmatic handling
            details: Optional additional details about the error
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class ServiceException(BaseAppException):
    """
    Exception raised by service layer operations.

    Used for business logic errors and service-level failures.
    """

    pass


class ValidationException(BaseAppException):
    """
    Exception raised for validation errors.

    Used when input data fails validation rules.
    """

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        """
        Initialize validation exception.

        Args:
            message: Error message
            field: The field that failed validation
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)
        self.field = field
        if field:
            self.details["field"] = field


class DatabaseException(BaseAppException):
    """
    Exception raised for database operation errors.

    Used for database connection issues, query failures, etc.
    """

    pass


class AuthenticationException(BaseAppException):
    """
    Exception raised for authentication failures.

    Used when authentication credentials are invalid or missing.
    """

    pass


class AuthorizationException(BaseAppException):
    """
    Exception raised for authorization failures.

    Used when a user doesn't have permission to perform an action.
    """

    def __init__(
        self, message: str, required_permission: Optional[str] = None, **kwargs
    ):
        """
        Initialize authorization exception.

        Args:
            message: Error message
            required_permission: The permission that was required
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)
        self.required_permission = required_permission
        if required_permission:
            self.details["required_permission"] = required_permission


class ExternalServiceException(BaseAppException):
    """
    Exception raised for external service failures.

    Used when external APIs or services are unavailable or return errors.
    """

    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        """
        Initialize external service exception.

        Args:
            message: Error message
            service_name: Name of the external service
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(message, **kwargs)
        self.service_name = service_name
        if service_name:
            self.details["service_name"] = service_name


class ConfigurationException(BaseAppException):
    """
    Exception raised for configuration errors.

    Used when application configuration is invalid or missing.
    """

    pass
