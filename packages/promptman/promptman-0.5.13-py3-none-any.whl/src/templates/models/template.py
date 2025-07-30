"""
Template data model for the AI Prompt Manager application.

This module defines the Template class that represents
template entities with proper validation and serialization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Template:
    """
    Template entity representing a prompt template in the system.

    This class encapsulates all template-related data and provides
    methods for template operations and validation.
    """

    # Required fields
    tenant_id: str
    user_id: str
    name: str
    description: str
    content: str

    # Optional fields with defaults
    id: Optional[int] = None
    category: str = "Custom"
    tags: str = ""
    variables: str = ""
    is_builtin: bool = False
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
            raise ValueError("Template name cannot be empty")

        if not self.content or not self.content.strip():
            raise ValueError("Template content cannot be empty")

        if not self.tenant_id:
            raise ValueError("Tenant ID is required")

        if not self.user_id:
            raise ValueError("User ID is required")

        # Validate name format (similar to prompt validation)
        import re

        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", self.name):
            raise ValueError(
                "Template name can only contain letters, numbers, spaces, "
                "hyphens, and underscores"
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
        self.updated_at = datetime.now(timezone.utc)

    @property
    def variable_list(self) -> List[str]:
        """Get variables as a list."""
        if not self.variables:
            return []
        return [var.strip() for var in self.variables.split(",") if var.strip()]

    @variable_list.setter
    def variable_list(self, variables: List[str]) -> None:
        """Set variables from a list."""
        self.variables = ", ".join(variables) if variables else ""
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
        """Update template content and timestamp."""
        self.content = content
        self.updated_at = datetime.now(timezone.utc)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the template."""
        current_tags = self.tag_list
        if tag not in current_tags:
            current_tags.append(tag)
            self.tag_list = current_tags

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the template."""
        current_tags = self.tag_list
        if tag in current_tags:
            current_tags.remove(tag)
            self.tag_list = current_tags

    def has_tag(self, tag: str) -> bool:
        """Check if template has a specific tag."""
        return tag in self.tag_list

    def add_variable(self, variable: str) -> None:
        """Add a variable to the template."""
        current_vars = self.variable_list
        if variable not in current_vars:
            current_vars.append(variable)
            self.variable_list = current_vars

    def remove_variable(self, variable: str) -> None:
        """Remove a variable from the template."""
        current_vars = self.variable_list
        if variable in current_vars:
            current_vars.remove(variable)
            self.variable_list = current_vars

    def has_variable(self, variable: str) -> bool:
        """Check if template has a specific variable."""
        return variable in self.variable_list

    def set_category(self, category: str) -> None:
        """Set template category."""
        self.category = category
        self.updated_at = datetime.now(timezone.utc)

    def mark_as_builtin(self, is_builtin: bool = True) -> None:
        """Mark or unmark template as builtin template."""
        self.is_builtin = is_builtin
        self.updated_at = datetime.now(timezone.utc)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Convert template to dictionary representation.

        Args:
            include_metadata: Whether to include metadata

        Returns:
            Dictionary representation of template
        """
        template_dict: Dict[str, Any] = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "tag_list": self.tag_list,
            "variables": self.variables,
            "variable_list": self.variable_list,
            "is_builtin": self.is_builtin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "content_length": self.content_length,
            "word_count": self.word_count,
        }

        if include_metadata:
            template_dict["metadata"] = self.metadata

        return template_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """
        Create Template from dictionary.

        Args:
            data: Dictionary containing template data

        Returns:
            Template instance
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
            description=data.get("description", ""),
            content=data["content"],
            category=data.get("category", "Custom"),
            tags=data.get("tags", ""),
            variables=data.get("variables", ""),
            is_builtin=data.get("is_builtin", False),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
        )

    def clone(
        self, new_name: Optional[str] = None, new_tenant_id: Optional[str] = None
    ) -> "Template":
        """
        Create a copy of this template.

        Args:
            new_name: New name for the cloned template
            new_tenant_id: New tenant ID for the cloned template

        Returns:
            New Template instance
        """
        cloned = Template(
            tenant_id=new_tenant_id or self.tenant_id,
            user_id=self.user_id,
            name=new_name or f"{self.name}_copy",
            description=self.description,
            content=self.content,
            category=self.category,
            tags=self.tags,
            variables=self.variables,
            is_builtin=False,  # Cloned templates are never builtin
            metadata=self.metadata.copy(),
        )

        # Clear ID and timestamps for new template
        cloned.id = None
        cloned.created_at = datetime.now(timezone.utc)
        cloned.updated_at = cloned.created_at

        return cloned

    def substitute_variables(self, substitutions: Dict[str, str]) -> str:
        """
        Substitute variables in template content.

        Args:
            substitutions: Dictionary mapping variable names to values

        Returns:
            Content with variables substituted
        """
        content = self.content
        for var_name, var_value in substitutions.items():
            # Replace {variable_name} with actual value
            content = content.replace(f"{{{var_name}}}", var_value)
        return content

    def extract_variables(self) -> List[str]:
        """
        Extract variable names from template content.

        Returns:
            List of variable names found in content
        """
        import re

        # Find all {variable_name} patterns
        pattern = r"\{([^}]+)\}"
        matches = re.findall(pattern, self.content)

        # Remove duplicates and sort
        variables = sorted(list(set(matches)))

        # Update the variables field if different
        if set(variables) != set(self.variable_list):
            self.variable_list = variables

        return variables

    def __str__(self) -> str:
        """String representation of template."""
        return (
            f"Template(name={self.name}, category={self.category}, "
            f"tenant={self.tenant_id})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of template."""
        return (
            f"Template(id={self.id}, name={self.name}, description={self.description}, "
            f"category={self.category}, tenant_id={self.tenant_id}, "
            f"user_id={self.user_id}, is_builtin={self.is_builtin})"
        )
