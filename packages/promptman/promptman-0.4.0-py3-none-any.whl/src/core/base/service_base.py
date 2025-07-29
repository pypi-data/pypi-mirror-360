"""
Base service class providing common functionality for all service layer components.

This module defines the base service architecture that all application services
should inherit from, providing consistent error handling, logging, and validation.
"""

import logging
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from ..exceptions.base import ServiceException, ValidationException

T = TypeVar("T")


@dataclass
class ServiceResult(Generic[T]):
    """
    Standard result object for service operations.

    Provides consistent structure for service method returns,
    including success/failure status, data, and error information.
    """

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    @classmethod
    def success_result(cls, data: T) -> "ServiceResult[T]":
        """Create a successful result."""
        return cls(success=True, data=data)

    @classmethod
    def error_result(
        cls,
        error: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> "ServiceResult[T]":
        """Create an error result."""
        return cls(success=False, error=error, error_code=error_code, details=details)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for API responses."""
        result = {"success": self.success, "timestamp": datetime.utcnow().isoformat()}

        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
            if self.error_code:
                result["error_code"] = self.error_code
            if self.details:
                result["details"] = self.details

        return result


class BaseService(ABC):
    """
    Base service class providing common functionality for all services.

    This class provides:
    - Standardized error handling and logging
    - Input validation framework
    - Common service patterns
    - Result formatting
    """

    def __init__(self, logger_name: Optional[str] = None):
        """
        Initialize the base service.

        Args:
            logger_name: Custom logger name. If None, uses class name.
        """
        self.logger = logging.getLogger(logger_name or self.__class__.__name__)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration for this service."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def handle_error(
        self, operation: str, error: Exception, details: Optional[Dict[str, Any]] = None
    ) -> ServiceResult[Any]:
        """
        Standardized error handling for service operations.

        Args:
            operation: Description of the operation that failed
            error: The exception that occurred
            details: Additional error details

        Returns:
            ServiceResult with error information
        """
        error_message = f"Failed to {operation}: {str(error)}"
        self.logger.error(error_message, exc_info=True)

        # Determine error code based on exception type
        error_code = None
        if isinstance(error, ValidationException):
            error_code = "VALIDATION_ERROR"
        elif isinstance(error, ServiceException):
            error_code = "SERVICE_ERROR"
        else:
            error_code = "INTERNAL_ERROR"

        return ServiceResult.error_result(
            error=error_message, error_code=error_code, details=details
        )

    def validate_required_fields(
        self, data: Dict[str, Any], required_fields: List[str]
    ) -> None:
        """
        Validate that required fields are present in data.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Raises:
            ValidationException: If any required fields are missing
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValidationException(
                f"Missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields},
            )

    def validate_field_types(
        self, data: Dict[str, Any], field_types: Dict[str, type]
    ) -> None:
        """
        Validate field types in data.

        Args:
            data: Data dictionary to validate
            field_types: Dictionary mapping field names to expected types

        Raises:
            ValidationException: If any fields have incorrect types
        """
        type_errors = []
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    type_errors.append(f"{field} must be {expected_type.__name__}")

        if type_errors:
            raise ValidationException(
                f"Type validation errors: {'; '.join(type_errors)}",
                details={"type_errors": type_errors},
            )

    def validate_string_length(
        self,
        text: str,
        field_name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> None:
        """
        Validate string length constraints.

        Args:
            text: String to validate
            field_name: Name of the field being validated
            min_length: Minimum allowed length
            max_length: Maximum allowed length

        Raises:
            ValidationException: If length constraints are violated
        """
        if min_length is not None and len(text) < min_length:
            raise ValidationException(
                f"{field_name} must be at least {min_length} characters long",
                field=field_name,
            )

        if max_length is not None and len(text) > max_length:
            raise ValidationException(
                f"{field_name} must be no more than {max_length} characters long",
                field=field_name,
            )

    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize input data by removing potentially harmful content.

        Args:
            data: Input data to sanitize

        Returns:
            Sanitized data dictionary
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Basic HTML/script tag removal for security
                value = value.replace("<script>", "").replace("</script>", "")
                value = value.replace("<", "&lt;").replace(">", "&gt;")
                value = value.strip()

            sanitized[key] = value

        return sanitized

    def log_operation(
        self,
        operation: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a service operation for audit purposes.

        Args:
            operation: Description of the operation
            user_id: ID of the user performing the operation
            tenant_id: ID of the tenant (for multi-tenant applications)
            details: Additional operation details
        """
        log_data: Dict[str, Any] = {
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "tenant_id": tenant_id,
        }

        if details:
            log_data["details"] = details

        self.logger.info(f"Operation: {operation}", extra=log_data)

    def paginate_results(
        self, items: List[T], page: int = 1, per_page: int = 50
    ) -> Dict[str, Any]:
        """
        Paginate a list of items.

        Args:
            items: List of items to paginate
            page: Page number (1-based)
            per_page: Number of items per page

        Returns:
            Dictionary with paginated results and metadata
        """
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page

        # Calculate start and end indices
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        paginated_items = items[start_idx:end_idx]

        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    def format_response(
        self, data: T, message: Optional[str] = None
    ) -> ServiceResult[T]:
        """
        Format a successful service response.

        Args:
            data: Response data
            message: Optional success message

        Returns:
            ServiceResult with formatted response
        """
        result = ServiceResult.success_result(data)
        if message:
            result.details = {"message": message}

        return result


class TenantAwareService(BaseService):
    """
    Service base class for multi-tenant aware services.

    Provides additional functionality for services that need to handle
    tenant-specific operations and data isolation.
    """

    def __init__(self, logger_name: Optional[str] = None):
        """Initialize tenant-aware service."""
        super().__init__(logger_name)
        self.current_tenant_id: Optional[str] = None
        self.current_user_id: Optional[str] = None

    def set_context(self, tenant_id: str, user_id: str) -> None:
        """
        Set the current tenant and user context.

        Args:
            tenant_id: Current tenant ID
            user_id: Current user ID
        """
        self.current_tenant_id = tenant_id
        self.current_user_id = user_id

        self.logger.debug(f"Context set - Tenant: {tenant_id}, User: {user_id}")

    def ensure_tenant_context(self) -> None:
        """
        Ensure that tenant context is set.

        Raises:
            ServiceException: If tenant context is not set
        """
        if not self.current_tenant_id:
            raise ServiceException(
                "Tenant context not set - call set_context() first",
                code="MISSING_TENANT_CONTEXT",
            )

    def validate_tenant_access(self, resource_tenant_id: str) -> None:
        """
        Validate that current tenant can access a resource.

        Args:
            resource_tenant_id: Tenant ID of the resource being accessed

        Raises:
            ServiceException: If tenant doesn't have access to the resource
        """
        self.ensure_tenant_context()

        if self.current_tenant_id != resource_tenant_id:
            raise ServiceException(
                "Access denied: Resource belongs to different tenant",
                code="TENANT_ACCESS_DENIED",
            )

    def get_tenant_filter(self) -> Dict[str, Optional[str]]:
        """
        Get tenant filter for database queries.

        Returns:
            Dictionary with tenant_id filter
        """
        self.ensure_tenant_context()
        return {"tenant_id": self.current_tenant_id}


class CachedService(BaseService):
    """
    Service base class with caching support.

    Provides basic caching functionality for services that need
    to cache frequently accessed data.
    """

    def __init__(self, logger_name: Optional[str] = None, cache_ttl: int = 300):
        """
        Initialize cached service.

        Args:
            logger_name: Custom logger name
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        super().__init__(logger_name)
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = cache_ttl

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return "|".join(key_parts)

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached item is still valid."""
        if key not in self.cache_timestamps:
            return False

        age = (datetime.utcnow() - self.cache_timestamps[key]).total_seconds()
        return age < self.cache_ttl

    def get_cached(self, key: str) -> Optional[Any]:
        """Get item from cache if valid."""
        if self._is_cache_valid(key):
            return self.cache.get(key)
        else:
            # Remove expired item
            self.cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
            return None

    def set_cached(self, key: str, value: Any) -> None:
        """Set item in cache."""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.utcnow()

    def clear_cache(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.cache_timestamps.clear()
