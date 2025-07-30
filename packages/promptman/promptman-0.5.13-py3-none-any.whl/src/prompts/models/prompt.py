"""
Prompt data model for the AI Prompt Manager application.

This module defines the Prompt class that represents
prompt entities with proper validation and serialization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import yaml


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
    visibility: str = "private"
    is_enhancement_prompt: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Set default timestamps
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

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
                "Prompt name can only contain letters, numbers, spaces, "
                "hyphens, and underscores"
            )

        # Validate visibility field
        if self.visibility not in ["private", "public"]:
            raise ValueError("Visibility must be either 'private' or 'public'")

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
        self.updated_at = datetime.now(timezone.utc)

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
        self.updated_at = datetime.now(timezone.utc)

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
        self.updated_at = datetime.now(timezone.utc)

    def mark_as_enhancement(self, is_enhancement: bool = True) -> None:
        """Mark or unmark prompt as enhancement prompt."""
        self.is_enhancement_prompt = is_enhancement
        self.updated_at = datetime.now(timezone.utc)

    def set_visibility(self, visibility: str) -> None:
        """Set prompt visibility."""
        if visibility not in ["private", "public"]:
            raise ValueError("Visibility must be either 'private' or 'public'")
        self.visibility = visibility
        self.updated_at = datetime.now(timezone.utc)

    def is_public(self) -> bool:
        """Check if prompt is public."""
        return self.visibility == "public"

    def is_private(self) -> bool:
        """Check if prompt is private."""
        return self.visibility == "private"

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value
        self.updated_at = datetime.now(timezone.utc)

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
            "visibility": self.visibility,
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
            visibility=data.get("visibility", "private"),
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
            visibility=data.get("visibility", "private"),
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
            "visibility": self.visibility,
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
            visibility=self.visibility,
            is_enhancement_prompt=self.is_enhancement_prompt,
            metadata=self.metadata.copy(),
        )

        # Clear ID and timestamps for new prompt
        cloned.id = None
        cloned.created_at = datetime.now(timezone.utc)
        cloned.updated_at = cloned.created_at

        return cloned

    def to_github_format(self) -> Dict[str, Any]:
        """
        Convert prompt to GitHub YAML format.

        Returns:
            Dictionary in GitHub YAML format
        """
        # Parse content to extract messages if it's in conversation format
        messages = self._parse_content_to_messages()

        github_dict = {
            "messages": messages,
            "model": self.get_metadata("model", "openai/gpt-4o"),
        }

        # Add optional fields if they exist
        if self.get_metadata("temperature"):
            github_dict["temperature"] = self.get_metadata("temperature")
        if self.get_metadata("max_tokens"):
            github_dict["max_tokens"] = self.get_metadata("max_tokens")
        if self.get_metadata("top_p"):
            github_dict["top_p"] = self.get_metadata("top_p")
        if self.get_metadata("frequency_penalty"):
            github_dict["frequency_penalty"] = self.get_metadata("frequency_penalty")
        if self.get_metadata("presence_penalty"):
            github_dict["presence_penalty"] = self.get_metadata("presence_penalty")

        return github_dict

    def _parse_content_to_messages(self) -> List[Dict[str, str]]:
        """
        Parse prompt content to extract messages in conversation format.

        Returns:
            List of message dictionaries
        """
        # Check if content is already in structured format
        if self.get_metadata("format") == "messages":
            messages = self.get_metadata("messages", [])
            if isinstance(messages, list):
                return messages
            return []

        # Try to parse as conversation format
        content = self.content.strip()
        messages = []

        # Check for explicit role markers
        if (
            "system:" in content.lower()
            or "user:" in content.lower()
            or "assistant:" in content.lower()
        ):
            lines = content.split("\n")
            current_role = None
            current_content = []

            for line in lines:
                line = line.strip()
                if line.lower().startswith("system:"):
                    if current_role and current_content:
                        messages.append(
                            {
                                "role": current_role,
                                "content": "\n".join(current_content).strip(),
                            }
                        )
                    current_role = "system"
                    current_content = [line[7:].strip()]
                elif line.lower().startswith("user:"):
                    if current_role and current_content:
                        messages.append(
                            {
                                "role": current_role,
                                "content": "\n".join(current_content).strip(),
                            }
                        )
                    current_role = "user"
                    current_content = [line[5:].strip()]
                elif line.lower().startswith("assistant:"):
                    if current_role and current_content:
                        messages.append(
                            {
                                "role": current_role,
                                "content": "\n".join(current_content).strip(),
                            }
                        )
                    current_role = "assistant"
                    current_content = [line[10:].strip()]
                else:
                    if current_role:
                        current_content.append(line)

            # Add the last message
            if current_role and current_content:
                messages.append(
                    {
                        "role": current_role,
                        "content": "\n".join(current_content).strip(),
                    }
                )

        # If no messages found, treat as single user message
        if not messages:
            messages = [
                {"role": "system", "content": ""},
                {"role": "user", "content": content},
            ]

        return messages

    @classmethod
    def from_github_format(
        cls,
        github_data: Dict[str, Any],
        tenant_id: str,
        user_id: str,
        name: Optional[str] = None,
        title: Optional[str] = None,
        category: str = "GitHub Import",
    ) -> "Prompt":
        """
        Create Prompt from GitHub YAML format.

        Args:
            github_data: Dictionary containing GitHub format data
            tenant_id: Tenant ID to assign
            user_id: User ID to assign
            name: Optional name for the prompt
            title: Optional title for the prompt
            category: Category for the prompt

        Returns:
            Prompt instance
        """
        messages = github_data.get("messages", [])

        # Convert messages to content string
        content_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if content.strip():  # Only add non-empty content
                content_parts.append(f"{role.upper()}: {content}")

        content = "\n\n".join(content_parts) if content_parts else ""

        # Generate name and title if not provided
        if not name:
            # Use first few words of first user message as name
            user_message = next(
                (msg for msg in messages if msg.get("role") == "user"), None
            )
            if user_message and user_message.get("content"):
                name = " ".join(user_message["content"].split()[:5])
                if len(name) > 50:
                    name = name[:47] + "..."
            else:
                name = "GitHub Import"

        if not title:
            title = name

        # Create metadata with GitHub-specific fields
        metadata = {
            "format": "messages",
            "messages": messages,
            "model": github_data.get("model", "openai/gpt-4o"),
            "source": "github_import",
        }

        # Add optional model parameters
        if "temperature" in github_data:
            metadata["temperature"] = github_data["temperature"]
        if "max_tokens" in github_data:
            metadata["max_tokens"] = github_data["max_tokens"]
        if "top_p" in github_data:
            metadata["top_p"] = github_data["top_p"]
        if "frequency_penalty" in github_data:
            metadata["frequency_penalty"] = github_data["frequency_penalty"]
        if "presence_penalty" in github_data:
            metadata["presence_penalty"] = github_data["presence_penalty"]

        return cls(
            tenant_id=tenant_id,
            user_id=user_id,
            name=name,
            title=title,
            content=content,
            category=category,
            tags="github,import",
            metadata=metadata,
        )

    def to_github_yaml(self) -> str:
        """
        Convert prompt to GitHub YAML format string.

        Returns:
            YAML string representation
        """
        github_dict = self.to_github_format()
        return yaml.dump(github_dict, default_flow_style=False, allow_unicode=True)

    @classmethod
    def from_github_yaml(
        cls,
        yaml_content: str,
        tenant_id: str,
        user_id: str,
        name: Optional[str] = None,
        title: Optional[str] = None,
        category: str = "GitHub Import",
    ) -> "Prompt":
        """
        Create Prompt from GitHub YAML format string.

        Args:
            yaml_content: YAML string content
            tenant_id: Tenant ID to assign
            user_id: User ID to assign
            name: Optional name for the prompt
            title: Optional title for the prompt
            category: Category for the prompt

        Returns:
            Prompt instance
        """
        try:
            github_data = yaml.safe_load(yaml_content)
            return cls.from_github_format(
                github_data, tenant_id, user_id, name, title, category
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")

    def __str__(self) -> str:
        """String representation of prompt."""
        return (
            f"Prompt(name={self.name}, category={self.category}, "
            f"tenant={self.tenant_id})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of prompt."""
        return (
            f"Prompt(id={self.id}, name={self.name}, title={self.title}, "
            f"category={self.category}, tenant_id={self.tenant_id}, "
            f"user_id={self.user_id}, is_enhancement={self.is_enhancement_prompt})"
        )
