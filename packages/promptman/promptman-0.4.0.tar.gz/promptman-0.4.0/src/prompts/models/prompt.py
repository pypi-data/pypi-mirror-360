"""
Prompt data model for the AI Prompt Manager application.

This module defines the Prompt class that represents
prompt entities with proper validation and serialization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Prompt:
    """
    Prompt entity representing an AI prompt in the system.

    This class encapsulates all prompt-related data and provides
    methods for prompt operations and validation.
    """

    # Required fields
    tenant_id: str
    user_id: str
    name: str
    title: str
    content: str

    # Optional fields with defaults
    id: Optional[int] = None
    category: str = "Uncategorized"
    tags: str = ""
    is_enhancement_prompt: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Set default timestamps
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        if self.updated_at is None:
            self.updated_at = self.created_at

        # Validate required fields
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Validate required fields and constraints."""
        if not self.name or not self.name.strip():
            raise ValueError("Prompt name cannot be empty")

        if not self.title or not self.title.strip():
            raise ValueError("Prompt title cannot be empty")

        if not self.content or not self.content.strip():
            raise ValueError("Prompt content cannot be empty")

        if not self.tenant_id:
            raise ValueError("Tenant ID is required")

        if not self.user_id:
            raise ValueError("User ID is required")

        # Validate name format (similar to legacy validation)
        import re

        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", self.name):
            raise ValueError(
                "Prompt name can only contain letters, numbers, spaces, hyphens, and underscores"
            )

    @property
    def tag_list(self) -> List[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @tag_list.setter
    def tag_list(self, tags: List[str]) -> None:
        """Set tags from a list."""
        self.tags = ", ".join(tags) if tags else ""
        self.updated_at = datetime.utcnow()

    @property
    def content_length(self) -> int:
        """Get content length in characters."""
        return len(self.content) if self.content else 0

    @property
    def word_count(self) -> int:
        """Get approximate word count."""
        if not self.content:
            return 0
        return len(self.content.split())

    def update_content(self, content: str) -> None:
        """Update prompt content and timestamp."""
        self.content = content
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the prompt."""
        current_tags = self.tag_list
        if tag not in current_tags:
            current_tags.append(tag)
            self.tag_list = current_tags

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the prompt."""
        current_tags = self.tag_list
        if tag in current_tags:
            current_tags.remove(tag)
            self.tag_list = current_tags

    def has_tag(self, tag: str) -> bool:
        """Check if prompt has a specific tag."""
        return tag in self.tag_list

    def set_category(self, category: str) -> None:
        """Set prompt category."""
        self.category = category
        self.updated_at = datetime.utcnow()

    def mark_as_enhancement(self, is_enhancement: bool = True) -> None:
        """Mark or unmark prompt as enhancement prompt."""
        self.is_enhancement_prompt = is_enhancement
        self.updated_at = datetime.utcnow()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Convert prompt to dictionary representation.

        Args:
            include_metadata: Whether to include metadata

        Returns:
            Dictionary representation of prompt
        """
        prompt_dict: Dict[str, Any] = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "name": self.name,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "tag_list": self.tag_list,
            "is_enhancement_prompt": self.is_enhancement_prompt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "content_length": self.content_length,
            "word_count": self.word_count,
        }

        if include_metadata:
            prompt_dict["metadata"] = self.metadata

        return prompt_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prompt":
        """
        Create Prompt from dictionary.

        Args:
            data: Dictionary containing prompt data

        Returns:
            Prompt instance
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
            tenant_id=data["tenant_id"],
            user_id=data["user_id"],
            name=data["name"],
            title=data["title"],
            content=data["content"],
            category=data.get("category", "Uncategorized"),
            tags=data.get("tags", ""),
            is_enhancement_prompt=data.get("is_enhancement_prompt", False),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_legacy_dict(
        cls, data: Dict[str, Any], tenant_id: str, user_id: str
    ) -> "Prompt":
        """
        Create Prompt from legacy dictionary format.

        Args:
            data: Legacy dictionary format
            tenant_id: Tenant ID to assign
            user_id: User ID to assign

        Returns:
            Prompt instance
        """
        return cls(
            id=data.get("id"),
            tenant_id=tenant_id,
            user_id=user_id,
            name=data["name"],
            title=data.get("title", data["name"]),  # Fallback to name if no title
            content=data["content"],
            category=data.get("category", "Uncategorized"),
            tags=data.get("tags", ""),
            is_enhancement_prompt=data.get("is_enhancement_prompt", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_legacy_dict(self) -> Dict[str, Any]:
        """
        Convert to legacy dictionary format for backward compatibility.

        Returns:
            Dictionary in legacy format
        """
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "is_enhancement_prompt": self.is_enhancement_prompt,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
        }

    def clone(
        self, new_name: Optional[str] = None, new_tenant_id: Optional[str] = None
    ) -> "Prompt":
        """
        Create a copy of this prompt.

        Args:
            new_name: New name for the cloned prompt
            new_tenant_id: New tenant ID for the cloned prompt

        Returns:
            New Prompt instance
        """
        cloned = Prompt(
            tenant_id=new_tenant_id or self.tenant_id,
            user_id=self.user_id,
            name=new_name or f"{self.name}_copy",
            title=self.title,
            content=self.content,
            category=self.category,
            tags=self.tags,
            is_enhancement_prompt=self.is_enhancement_prompt,
            metadata=self.metadata.copy(),
        )

        # Clear ID and timestamps for new prompt
        cloned.id = None
        cloned.created_at = datetime.utcnow()
        cloned.updated_at = cloned.created_at

        return cloned

    def __str__(self) -> str:
        """String representation of prompt."""
        return f"Prompt(name={self.name}, category={self.category}, tenant={self.tenant_id})"

    def __repr__(self) -> str:
        """Detailed string representation of prompt."""
        return (
            f"Prompt(id={self.id}, name={self.name}, title={self.title}, "
            f"category={self.category}, tenant_id={self.tenant_id}, "
            f"user_id={self.user_id}, is_enhancement={self.is_enhancement_prompt})"
        )
