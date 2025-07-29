"""
Custom exception classes for the AI Prompt Manager application.
"""

from .base import (
    AuthenticationException,
    AuthorizationException,
    BaseAppException,
    DatabaseException,
    ServiceException,
    ValidationException,
)

__all__ = [
    "BaseAppException",
    "ServiceException",
    "ValidationException",
    "DatabaseException",
    "AuthenticationException",
    "AuthorizationException",
]
