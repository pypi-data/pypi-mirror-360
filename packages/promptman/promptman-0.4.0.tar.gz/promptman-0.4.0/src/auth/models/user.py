"""
User data model for the AI Prompt Manager application.

This module defines the User class and related enums that represent
user entities in the system with proper type hints and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class UserRole(Enum):
    """User roles defining access levels."""

    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


@dataclass
class User:
    """
    User entity representing a system user.

    This class encapsulates all user-related data and provides
    methods for user operations and validation.
    """

    # Required fields
    tenant_id: str
    email: str
    password_hash: str
    salt: str
    first_name: str
    last_name: str
    role: UserRole

    # Optional fields
    id: Optional[str] = None
    sso_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure role is UserRole enum
        if isinstance(self.role, str):
            self.role = UserRole(self.role)

        # Set default timestamps
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        if self.updated_at is None:
            self.updated_at = self.created_at

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self) -> str:
        """Get user's display name (full name or email if names are empty)."""
        full_name = self.full_name
        return full_name if full_name else self.email

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    @property
    def is_readonly(self) -> bool:
        """Check if user has readonly role."""
        return self.role == UserRole.READONLY

    @property
    def can_write(self) -> bool:
        """Check if user can write data."""
        return self.role in [UserRole.ADMIN, UserRole.USER]

    @property
    def can_admin(self) -> bool:
        """Check if user can perform admin operations."""
        return self.role == UserRole.ADMIN

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: Permission to check

        Returns:
            True if user has permission
        """
        # Define permission mappings
        permissions = {
            UserRole.ADMIN: [
                "read",
                "write",
                "delete",
                "admin",
                "manage_users",
                "manage_tenants",
                "view_analytics",
            ],
            UserRole.USER: ["read", "write", "delete_own"],
            UserRole.READONLY: ["read"],
        }

        user_permissions = permissions.get(self.role, [])
        return permission in user_permissions

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.

        Args:
            include_sensitive: Whether to include sensitive fields

        Returns:
            Dictionary representation of user
        """
        user_dict = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }

        if include_sensitive:
            user_dict.update(
                {
                    "password_hash": self.password_hash,
                    "salt": self.salt,
                    "sso_id": self.sso_id,
                }
            )

        return user_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """
        Create User from dictionary.

        Args:
            data: Dictionary containing user data

        Returns:
            User instance
        """
        # Handle datetime fields
        created_at = None
        if data.get("created_at"):
            if isinstance(data["created_at"], str):
                created_at = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            elif isinstance(data["created_at"], datetime):
                created_at = data["created_at"]

        last_login = None
        if data.get("last_login"):
            if isinstance(data["last_login"], str):
                last_login = datetime.fromisoformat(
                    data["last_login"].replace("Z", "+00:00")
                )
            elif isinstance(data["last_login"], datetime):
                last_login = data["last_login"]

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(
                    data["updated_at"].replace("Z", "+00:00")
                )
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        # Handle role field
        role = data["role"]
        if isinstance(role, str):
            role = UserRole(role)

        return cls(
            id=data.get("id"),
            tenant_id=data["tenant_id"],
            email=data["email"],
            password_hash=data.get("password_hash", ""),
            salt=data.get("salt", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=role,
            sso_id=data.get("sso_id"),
            is_active=data.get("is_active", True),
            created_at=created_at,
            last_login=last_login,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        """String representation of user."""
        return (
            f"User(email={self.email}, role={self.role.value}, tenant={self.tenant_id})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of user."""
        return (
            f"User(id={self.id}, email={self.email}, role={self.role.value}, "
            f"tenant_id={self.tenant_id}, is_active={self.is_active})"
        )
