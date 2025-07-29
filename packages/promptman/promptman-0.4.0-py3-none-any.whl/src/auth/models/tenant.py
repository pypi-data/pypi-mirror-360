"""
Tenant data model for the AI Prompt Manager application.

This module defines the Tenant class that represents
tenant entities in the multi-tenant system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Tenant:
    """
    Tenant entity representing an organization in the multi-tenant system.

    This class encapsulates all tenant-related data and provides
    methods for tenant operations and validation.
    """

    # Required fields
    name: str
    subdomain: str

    # Optional fields
    id: Optional[str] = None
    max_users: int = 100
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Configuration and metadata
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Set default timestamps
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        if self.updated_at is None:
            self.updated_at = self.created_at

        # Validate subdomain format
        self._validate_subdomain()

    def _validate_subdomain(self) -> None:
        """Validate subdomain format."""
        import re

        if not self.subdomain:
            raise ValueError("Subdomain cannot be empty")

        # Check subdomain format (alphanumeric and hyphens, no spaces)
        if not re.match(r"^[a-zA-Z0-9-]+$", self.subdomain):
            raise ValueError("Subdomain can only contain letters, numbers, and hyphens")

        # Cannot start or end with hyphen
        if self.subdomain.startswith("-") or self.subdomain.endswith("-"):
            raise ValueError("Subdomain cannot start or end with hyphen")

        # Length constraints
        if len(self.subdomain) < 2:
            raise ValueError("Subdomain must be at least 2 characters long")

        if len(self.subdomain) > 63:
            raise ValueError("Subdomain must be no more than 63 characters long")

    @property
    def is_default_tenant(self) -> bool:
        """Check if this is the default tenant (localhost)."""
        return self.subdomain == "localhost"

    @property
    def user_limit_reached(self) -> bool:
        """Check if tenant has reached user limit (requires user count)."""
        # This would need to be implemented with actual user count
        # For now, return False as placeholder
        return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get tenant setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Set tenant setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
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

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def can_add_user(self) -> bool:
        """
        Check if tenant can add more users.

        Returns:
            True if tenant can add users
        """
        # This would need actual user count implementation
        # For now, just check if active and under limit
        return self.is_active and not self.user_limit_reached

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tenant to dictionary representation.

        Returns:
            Dictionary representation of tenant
        """
        return {
            "id": self.id,
            "name": self.name,
            "subdomain": self.subdomain,
            "max_users": self.max_users,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "settings": self.settings,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tenant":
        """
        Create Tenant from dictionary.

        Args:
            data: Dictionary containing tenant data

        Returns:
            Tenant instance
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

        updated_at = None
        if data.get("updated_at"):
            if isinstance(data["updated_at"], str):
                updated_at = datetime.fromisoformat(
                    data["updated_at"].replace("Z", "+00:00")
                )
            elif isinstance(data["updated_at"], datetime):
                updated_at = data["updated_at"]

        return cls(
            id=data.get("id"),
            name=data["name"],
            subdomain=data["subdomain"],
            max_users=data.get("max_users", 100),
            is_active=data.get("is_active", True),
            created_at=created_at,
            updated_at=updated_at,
            settings=data.get("settings", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def create_default_tenant(cls) -> "Tenant":
        """
        Create the default localhost tenant.

        Returns:
            Default tenant instance
        """
        return cls(
            name="Default Tenant", subdomain="localhost", max_users=1000, is_active=True
        )

    def __str__(self) -> str:
        """String representation of tenant."""
        return f"Tenant(name={self.name}, subdomain={self.subdomain})"

    def __repr__(self) -> str:
        """Detailed string representation of tenant."""
        return (
            f"Tenant(id={self.id}, name={self.name}, subdomain={self.subdomain}, "
            f"max_users={self.max_users}, is_active={self.is_active})"
        )
