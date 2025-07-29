"""
Prompt service implementing business logic for prompt management.

This module provides the service layer for prompt operations, handling
validation, business rules, and coordination between components.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...core.base.database_manager import BaseDatabaseManager
from ...core.base.service_base import BaseService, ServiceResult
from ...core.exceptions.base import ValidationException
from ..models.prompt import Prompt
from ..repositories.prompt_repository import PromptRepository
from .template_service import TemplateService


class PromptService(BaseService):
    """
    Service for prompt business logic and operations.

    Provides high-level operations for prompt management with
    proper validation, authorization, and business rule enforcement.
    """

    def __init__(self, db_manager: BaseDatabaseManager):
        """Initialize prompt service."""
        super().__init__()
        self.db_manager = db_manager
        self.repository = PromptRepository(db_manager)
        self.template_service = TemplateService()

    def create_prompt(
        self,
        tenant_id: str,
        user_id: str,
        name: str,
        title: str,
        content: str,
        category: str = "Uncategorized",
        tags: str = "",
        is_enhancement_prompt: bool = False,
    ) -> ServiceResult[Prompt]:
        """
        Create a new prompt.

        Args:
            tenant_id: Tenant context
            user_id: User creating the prompt
            name: Unique prompt name
            title: Display title
            content: Prompt content
            category: Category classification
            tags: Comma-separated tags
            is_enhancement_prompt: Whether this is an enhancement prompt

        Returns:
            ServiceResult containing the created prompt or error
        """
        try:
            # Set tenant context
            self.repository.set_tenant_context(tenant_id)

            # Validate inputs
            validation_result = self._validate_prompt_data(name, title, content)
            if not validation_result.success:
                return ServiceResult(
                    success=False,
                    error=validation_result.error,
                    error_code=validation_result.error_code,
                )

            # Check for duplicate name
            if self.repository.name_exists(name.strip()):
                return ServiceResult(
                    success=False,
                    error=f"A prompt with name '{name}' already exists in your workspace",
                    error_code="DUPLICATE_NAME",
                )

            # Create prompt entity
            prompt = Prompt(
                tenant_id=tenant_id,
                user_id=user_id,
                name=name.strip(),
                title=title.strip(),
                content=content.strip(),
                category=category.strip() or "Uncategorized",
                tags=tags.strip(),
                is_enhancement_prompt=is_enhancement_prompt,
            )

            # Save to repository
            saved_prompt = self.repository.save(prompt)

            if saved_prompt:
                return ServiceResult(success=True, data=saved_prompt)
            else:
                return ServiceResult(
                    success=False,
                    error="Failed to create prompt",
                    error_code="CREATE_FAILED",
                )

        except ValidationException as e:
            return ServiceResult(
                success=False, error=str(e), error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            self.logger.error(f"Error creating prompt: {e}")
            import traceback

            traceback.print_exc()
            return ServiceResult(
                success=False,
                error=f"An unexpected error occurred while creating the prompt: {str(e)}",
                error_code="INTERNAL_ERROR",
            )

    def update_prompt(
        self,
        tenant_id: str,
        user_id: str,
        original_name: str,
        new_name: str,
        title: str,
        content: str,
        category: str = "Uncategorized",
        tags: str = "",
        is_enhancement_prompt: bool = False,
    ) -> ServiceResult[Prompt]:
        """
        Update an existing prompt.

        Args:
            tenant_id: Tenant context
            user_id: User updating the prompt
            original_name: Current prompt name
            new_name: New prompt name
            title: Updated title
            content: Updated content
            category: Updated category
            tags: Updated tags
            is_enhancement_prompt: Updated enhancement flag

        Returns:
            ServiceResult containing the updated prompt or error
        """
        try:
            # Set tenant context
            self.repository.set_tenant_context(tenant_id)

            # Validate inputs
            validation_result = self._validate_prompt_data(new_name, title, content)
            if not validation_result.success:
                return ServiceResult(
                    success=False,
                    error=validation_result.error,
                    error_code=validation_result.error_code,
                )

            # Find existing prompt
            existing_prompt = self.repository.find_by_name(original_name.strip())
            if not existing_prompt:
                return ServiceResult(
                    success=False,
                    error=f"Prompt '{original_name}' not found in your workspace",
                    error_code="NOT_FOUND",
                )

            # Check name change conflicts
            if original_name.strip() != new_name.strip():
                if self.repository.name_exists(
                    new_name.strip(), exclude_id=existing_prompt.id
                ):
                    return ServiceResult(
                        success=False,
                        error=f"A prompt with name '{new_name}' already exists in your workspace",
                        error_code="DUPLICATE_NAME",
                    )

            # Update prompt data
            existing_prompt.name = new_name.strip()
            existing_prompt.title = title.strip()
            existing_prompt.content = content.strip()
            existing_prompt.category = category.strip() or "Uncategorized"
            existing_prompt.tags = tags.strip()
            existing_prompt.is_enhancement_prompt = is_enhancement_prompt
            existing_prompt.updated_at = datetime.utcnow()

            # Save changes
            updated_prompt = self.repository.save(existing_prompt)

            if updated_prompt:
                return ServiceResult(success=True, data=updated_prompt)
            else:
                return ServiceResult(
                    success=False,
                    error="Failed to update prompt",
                    error_code="UPDATE_FAILED",
                )

        except ValidationException as e:
            return ServiceResult(
                success=False, error=str(e), error_code="VALIDATION_ERROR"
            )
        except Exception as e:
            self.logger.error(f"Error updating prompt: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while updating the prompt",
                error_code="INTERNAL_ERROR",
            )

    def delete_prompt(self, tenant_id: str, name: str) -> ServiceResult[bool]:
        """
        Delete a prompt by name.

        Args:
            tenant_id: Tenant context
            name: Name of prompt to delete

        Returns:
            ServiceResult indicating success or failure
        """
        try:
            # Set tenant context
            self.repository.set_tenant_context(tenant_id)

            # Validate name
            if not name or not name.strip():
                return ServiceResult(
                    success=False,
                    error="Prompt name is required",
                    error_code="VALIDATION_ERROR",
                )

            # Check if prompt exists
            existing_prompt = self.repository.find_by_name(name.strip())
            if not existing_prompt:
                return ServiceResult(
                    success=False,
                    error=f"Prompt '{name}' not found in your workspace",
                    error_code="NOT_FOUND",
                )

            # Delete prompt
            deleted = self.repository.delete_by_name(name.strip())

            if deleted:
                return ServiceResult(success=True, data=True)
            else:
                return ServiceResult(
                    success=False,
                    error="Failed to delete prompt",
                    error_code="DELETE_FAILED",
                )

        except Exception as e:
            self.logger.error(f"Error deleting prompt: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while deleting the prompt",
                error_code="INTERNAL_ERROR",
            )

    def get_prompt_by_name(self, tenant_id: str, name: str) -> ServiceResult[Prompt]:
        """
        Get a prompt by name.

        Args:
            tenant_id: Tenant context
            name: Name of prompt to retrieve

        Returns:
            ServiceResult containing the prompt or error
        """
        try:
            # Set tenant context
            self.repository.set_tenant_context(tenant_id)

            if not name or not name.strip():
                return ServiceResult(
                    success=False,
                    error="Prompt name is required",
                    error_code="VALIDATION_ERROR",
                )

            prompt = self.repository.find_by_name(name.strip())

            if prompt:
                return ServiceResult(success=True, data=prompt)
            else:
                return ServiceResult(
                    success=False,
                    error=f"Prompt '{name}' not found",
                    error_code="NOT_FOUND",
                )

        except Exception as e:
            self.logger.error(f"Error retrieving prompt: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving the prompt",
                error_code="INTERNAL_ERROR",
            )

    def get_all_prompts(
        self,
        tenant_id: str,
        include_enhancement_prompts: bool = True,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ServiceResult[List[Prompt]]:
        """
        Get all prompts with optional filtering.

        Args:
            tenant_id: Tenant context
            include_enhancement_prompts: Whether to include enhancement prompts
            category: Optional category filter
            user_id: Optional user filter

        Returns:
            ServiceResult containing list of prompts
        """
        try:
            # Set tenant context
            self.repository.set_tenant_context(tenant_id)

            # Build filters
            filters: Dict[str, Any] = {}
            if not include_enhancement_prompts:
                filters["is_enhancement_prompt"] = False
            if category and category != "All":
                filters["category"] = category
            if user_id:
                filters["user_id"] = user_id

            # Get prompts
            prompts = self.repository.find_all(
                filters=filters, order_by="category, name"
            )

            return ServiceResult(success=True, data=prompts)

        except Exception as e:
            self.logger.error(f"Error retrieving prompts: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving prompts",
                error_code="INTERNAL_ERROR",
            )

    def get_enhancement_prompts(self, tenant_id: str) -> ServiceResult[List[Prompt]]:
        """
        Get all enhancement prompts.

        Args:
            tenant_id: Tenant context

        Returns:
            ServiceResult containing list of enhancement prompts
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            prompts = self.repository.find_enhancement_prompts()

            return ServiceResult(success=True, data=prompts)

        except Exception as e:
            self.logger.error(f"Error retrieving enhancement prompts: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving enhancement prompts",
                error_code="INTERNAL_ERROR",
            )

    def search_prompts(
        self,
        tenant_id: str,
        search_term: str,
        search_in: Optional[List[str]] = None,
        include_enhancement_prompts: bool = True,
        limit: Optional[int] = None,
    ) -> ServiceResult[List[Prompt]]:
        """
        Search prompts by content.

        Args:
            tenant_id: Tenant context
            search_term: Term to search for
            search_in: Fields to search in
            include_enhancement_prompts: Whether to include enhancement prompts
            limit: Maximum number of results

        Returns:
            ServiceResult containing matching prompts
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            if not search_term or not search_term.strip():
                # Return all prompts if no search term
                return self.get_all_prompts(tenant_id, include_enhancement_prompts)

            prompts = self.repository.search_prompts(
                search_term.strip(), search_in=search_in, limit=limit
            )

            # Filter out enhancement prompts if not requested
            if not include_enhancement_prompts:
                prompts = [p for p in prompts if not p.is_enhancement_prompt]

            return ServiceResult(success=True, data=prompts)

        except Exception as e:
            self.logger.error(f"Error searching prompts: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while searching prompts",
                error_code="INTERNAL_ERROR",
            )

    def get_categories(self, tenant_id: str) -> ServiceResult[List[str]]:
        """
        Get all categories in use.

        Args:
            tenant_id: Tenant context

        Returns:
            ServiceResult containing list of categories
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            categories = self.repository.get_categories()

            return ServiceResult(success=True, data=categories)

        except Exception as e:
            self.logger.error(f"Error retrieving categories: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving categories",
                error_code="INTERNAL_ERROR",
            )

    def get_tags(self, tenant_id: str) -> ServiceResult[List[str]]:
        """
        Get all tags in use.

        Args:
            tenant_id: Tenant context

        Returns:
            ServiceResult containing list of tags
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            tags = self.repository.get_tags()

            return ServiceResult(success=True, data=tags)

        except Exception as e:
            self.logger.error(f"Error retrieving tags: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving tags",
                error_code="INTERNAL_ERROR",
            )

    def get_statistics(self, tenant_id: str) -> ServiceResult[Dict[str, Any]]:
        """
        Get prompt statistics.

        Args:
            tenant_id: Tenant context

        Returns:
            ServiceResult containing statistics
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            stats = self.repository.get_statistics()

            return ServiceResult(success=True, data=stats)

        except Exception as e:
            self.logger.error(f"Error retrieving statistics: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving statistics",
                error_code="INTERNAL_ERROR",
            )

    def get_recent_prompts(
        self, tenant_id: str, limit: int = 10
    ) -> ServiceResult[List[Prompt]]:
        """
        Get recently created prompts.

        Args:
            tenant_id: Tenant context
            limit: Maximum number of prompts

        Returns:
            ServiceResult containing recent prompts
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            prompts = self.repository.get_recent_prompts(limit)

            return ServiceResult(success=True, data=prompts)

        except Exception as e:
            self.logger.error(f"Error retrieving recent prompts: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving recent prompts",
                error_code="INTERNAL_ERROR",
            )

    def duplicate_prompt(
        self, tenant_id: str, user_id: str, original_name: str, new_name: str
    ) -> ServiceResult[Prompt]:
        """
        Duplicate an existing prompt with a new name.

        Args:
            tenant_id: Tenant context
            user_id: User duplicating the prompt
            original_name: Name of prompt to duplicate
            new_name: Name for the new prompt

        Returns:
            ServiceResult containing the duplicated prompt
        """
        try:
            self.repository.set_tenant_context(tenant_id)

            # Get original prompt
            original_prompt = self.repository.find_by_name(original_name.strip())
            if not original_prompt:
                return ServiceResult(
                    success=False,
                    error=f"Prompt '{original_name}' not found",
                    error_code="NOT_FOUND",
                )

            # Check for name conflicts
            if self.repository.name_exists(new_name.strip()):
                return ServiceResult(
                    success=False,
                    error=f"A prompt with name '{new_name}' already exists",
                    error_code="DUPLICATE_NAME",
                )

            # Clone the prompt
            cloned_prompt = original_prompt.clone(new_name=new_name.strip())
            cloned_prompt.user_id = user_id

            # Save the clone
            saved_prompt = self.repository.save(cloned_prompt)

            if saved_prompt:
                return ServiceResult(success=True, data=saved_prompt)
            else:
                return ServiceResult(
                    success=False,
                    error="Failed to duplicate prompt",
                    error_code="CREATE_FAILED",
                )

        except Exception as e:
            self.logger.error(f"Error duplicating prompt: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while duplicating the prompt",
                error_code="INTERNAL_ERROR",
            )

    def _validate_prompt_data(
        self, name: str, title: str, content: str
    ) -> ServiceResult[bool]:
        """
        Validate prompt data.

        Args:
            name: Prompt name
            title: Prompt title
            content: Prompt content

        Returns:
            ServiceResult indicating validation success or failure
        """
        if not name or not name.strip():
            return ServiceResult(
                success=False,
                error="Prompt name is required",
                error_code="VALIDATION_ERROR",
            )

        if not title or not title.strip():
            return ServiceResult(
                success=False,
                error="Prompt title is required",
                error_code="VALIDATION_ERROR",
            )

        if not content or not content.strip():
            return ServiceResult(
                success=False,
                error="Prompt content is required",
                error_code="VALIDATION_ERROR",
            )

        # Validate name format
        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", name.strip()):
            return ServiceResult(
                success=False,
                error="Prompt name can only contain letters, numbers, spaces, hyphens, and underscores",
                error_code="VALIDATION_ERROR",
            )

        return ServiceResult(success=True, data=True)

    def apply_template_to_prompt(
        self,
        template_name: str,
        content: str,
        category: str = "Uncategorized",
        tags: str = "",
        user_context: str = "",
    ) -> ServiceResult[str]:
        """
        Apply a template to prompt content.

        Args:
            template_name: Name of the template to use
            content: Prompt content
            category: Prompt category
            tags: Prompt tags
            user_context: Additional user context

        Returns:
            ServiceResult containing the templated prompt
        """
        try:
            # Prepare template variables
            variables = {
                "content": content,
                "category": category,
                "tags": tags,
                "user_context": user_context,
            }

            # Apply template
            template_result = self.template_service.apply_template(
                template_name, variables, fallback_template="default"
            )

            if template_result.success:
                return ServiceResult(success=True, data=template_result.data)
            else:
                return ServiceResult(
                    success=False,
                    error=f"Template application failed: {template_result.error}",
                    error_code="TEMPLATE_ERROR",
                )

        except Exception as e:
            self.logger.error(f"Error applying template to prompt: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while applying template",
                error_code="INTERNAL_ERROR",
            )

    def enhance_prompt_with_template(
        self,
        original_prompt: str,
        enhancement_instructions: str = "",
        target_model: str = "",
        category: str = "Enhancement",
    ) -> ServiceResult[str]:
        """
        Enhance a prompt using enhancement template.

        Args:
            original_prompt: Original prompt to enhance
            enhancement_instructions: Specific enhancement directions
            target_model: Target AI model for optimization
            category: Enhancement category

        Returns:
            ServiceResult containing the enhanced prompt
        """
        try:
            # Prepare enhancement template variables
            variables = {
                "original_prompt": original_prompt,
                "enhancement_instructions": enhancement_instructions,
                "target_model": target_model,
                "category": category,
                "user_context": "",
            }

            # Apply enhancement template
            template_result = self.template_service.apply_template(
                "enhancement", variables, fallback_template="default"
            )

            if template_result.success:
                return ServiceResult(success=True, data=template_result.data)
            else:
                return ServiceResult(
                    success=False,
                    error=f"Enhancement template failed: {template_result.error}",
                    error_code="ENHANCEMENT_ERROR",
                )

        except Exception as e:
            self.logger.error(f"Error enhancing prompt with template: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while enhancing prompt",
                error_code="INTERNAL_ERROR",
            )

    def get_available_templates(self) -> ServiceResult[List[str]]:
        """
        Get list of available prompt templates.

        Returns:
            ServiceResult containing list of template names
        """
        try:
            return self.template_service.get_available_templates()

        except Exception as e:
            self.logger.error(f"Error getting available templates: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while retrieving templates",
                error_code="INTERNAL_ERROR",
            )

    def validate_template(self, template_content: str) -> ServiceResult[Dict[str, Any]]:
        """
        Validate template content.

        Args:
            template_content: Template content to validate

        Returns:
            ServiceResult containing validation results
        """
        try:
            return self.template_service.validate_template(template_content)

        except Exception as e:
            self.logger.error(f"Error validating template: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while validating template",
                error_code="INTERNAL_ERROR",
            )

    def create_custom_template(
        self, name: str, content: str, category: str = "custom"
    ) -> ServiceResult[str]:
        """
        Create a custom template.

        Args:
            name: Template name
            content: Template content
            category: Template category

        Returns:
            ServiceResult containing template path
        """
        try:
            return self.template_service.create_custom_template(name, content, category)

        except Exception as e:
            self.logger.error(f"Error creating custom template: {e}")
            return ServiceResult(
                success=False,
                error="An unexpected error occurred while creating template",
                error_code="INTERNAL_ERROR",
            )
