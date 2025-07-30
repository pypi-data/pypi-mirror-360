"""
Template service for managing prompt templates.

This module provides functionality for loading, validating, and applying
prompt templates with variable substitution and customization support.
"""

import os
import re
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional

from ...core.base.service_base import BaseService, ServiceResult
from ...core.config.settings import get_config


class TemplateService(BaseService):
    """
    Service for template management and processing.

    Handles template loading, validation, variable substitution,
    and customization for prompt generation and enhancement.
    """

    def __init__(self):
        """Initialize template service."""
        super().__init__()
        self.config = get_config()
        self.templates_dir = Path(__file__).parent.parent.parent.parent / "templates"
        self._template_cache: Dict[str, str] = {}

        # Default template mappings
        self.default_templates = {
            "default": "default_prompt_template.txt",
            "enhancement": "enhancement_template.txt",
            "business": "business_template.txt",
            "technical": "technical_template.txt",
            "creative": "creative_template.txt",
            "analytical": "analytical_template.txt",
        }

    def load_template(self, template_name: str) -> ServiceResult[str]:
        """
        Load a template by name.

        Args:
            template_name: Name of the template to load

        Returns:
            ServiceResult containing the template content
        """
        try:
            # Check cache first
            if template_name in self._template_cache:
                return ServiceResult(
                    success=True, data=self._template_cache[template_name]
                )

            # Determine template file path
            template_path = self._get_template_path(template_name)
            if not template_path:
                return ServiceResult(
                    success=False,
                    error=f"Template '{template_name}' not found",
                    error_code="TEMPLATE_NOT_FOUND",
                )

            # Load template content
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Cache the template
                self._template_cache[template_name] = content

                return ServiceResult(success=True, data=content)

            except FileNotFoundError:
                return ServiceResult(
                    success=False,
                    error=f"Template file not found: {template_path}",
                    error_code="FILE_NOT_FOUND",
                )
            except IOError as e:
                return ServiceResult(
                    success=False,
                    error=f"Error reading template file: {e}",
                    error_code="FILE_READ_ERROR",
                )

        except Exception as e:
            self.logger.error(f"Error loading template '{template_name}': {e}")
            return ServiceResult(
                success=False,
                error=f"Failed to load template: {str(e)}",
                error_code="TEMPLATE_LOAD_ERROR",
            )

    def apply_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        fallback_template: Optional[str] = None,
    ) -> ServiceResult[str]:
        """
        Apply a template with variable substitution.

        Args:
            template_name: Name of the template to use
            variables: Variables for substitution
            fallback_template: Fallback template if primary fails

        Returns:
            ServiceResult containing the rendered template
        """
        try:
            # Load the template
            template_result = self.load_template(template_name)
            if not template_result.success:
                # Try fallback template if specified
                if fallback_template:
                    template_result = self.load_template(fallback_template)
                    if not template_result.success:
                        return template_result
                else:
                    return template_result

            template_content = template_result.data
            if template_content is None:
                return ServiceResult(success=False, error="Template content is empty")

            # Apply variable substitution
            rendered_result = self._substitute_variables(template_content, variables)
            if not rendered_result.success:
                return rendered_result

            return ServiceResult(success=True, data=rendered_result.data)

        except Exception as e:
            self.logger.error(f"Error applying template '{template_name}': {e}")
            return ServiceResult(
                success=False,
                error=f"Failed to apply template: {str(e)}",
                error_code="TEMPLATE_APPLY_ERROR",
            )

    def get_available_templates(self) -> ServiceResult[List[str]]:
        """
        Get list of available templates.

        Returns:
            ServiceResult containing list of template names
        """
        try:
            templates: List[str] = []

            # Add default templates
            templates.extend(self.default_templates.keys())

            # Scan templates directory for additional templates
            if self.templates_dir.exists():
                for file_path in self.templates_dir.glob("*.txt"):
                    template_name = file_path.stem
                    if template_name not in [
                        self.default_templates.get(k, "").replace(".txt", "")
                        for k in self.default_templates
                    ]:
                        templates.append(template_name)

            return ServiceResult(success=True, data=sorted(templates))

        except Exception as e:
            self.logger.error(f"Error getting available templates: {e}")
            return ServiceResult(
                success=False,
                error=f"Failed to get templates: {str(e)}",
                error_code="TEMPLATE_LIST_ERROR",
            )

    def validate_template(self, template_content: str) -> ServiceResult[Dict[str, Any]]:
        """
        Validate template content and extract variables.

        Args:
            template_content: Template content to validate

        Returns:
            ServiceResult containing validation results
        """
        try:
            # Extract variables from template
            variables = self._extract_template_variables(template_content)

            # Basic validation
            validation_issues = []

            # Check for empty content
            if not template_content.strip():
                validation_issues.append("Template content is empty")

            # Check for unclosed braces
            open_braces = template_content.count("{")
            close_braces = template_content.count("}")
            if open_braces != close_braces:
                validation_issues.append("Mismatched braces in template")

            # Check for invalid variable names
            for var in variables:
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
                    validation_issues.append(f"Invalid variable name: {var}")

            validation_result = {
                "valid": len(validation_issues) == 0,
                "issues": validation_issues,
                "variables": variables,
                "variable_count": len(variables),
            }

            return ServiceResult(success=True, data=validation_result)

        except Exception as e:
            self.logger.error(f"Error validating template: {e}")
            return ServiceResult(
                success=False,
                error=f"Template validation failed: {str(e)}",
                error_code="TEMPLATE_VALIDATION_ERROR",
            )

    def create_custom_template(
        self, name: str, content: str, category: str = "custom"
    ) -> ServiceResult[str]:
        """
        Create a custom template file.

        Args:
            name: Template name
            content: Template content
            category: Template category

        Returns:
            ServiceResult containing the template path
        """
        try:
            # Validate template content
            validation_result = self.validate_template(content)
            if not validation_result.success:
                return ServiceResult(
                    success=False,
                    error=validation_result.error or "Template validation failed",
                    error_code=validation_result.error_code or "VALIDATION_ERROR",
                )

            if validation_result.data and not validation_result.data.get("valid", True):
                issues = validation_result.data.get(
                    "issues", ["Unknown validation error"]
                )
                return ServiceResult(
                    success=False,
                    error=f"Template validation failed: {', '.join(issues)}",
                    error_code="TEMPLATE_INVALID",
                )

            # Create template file path
            template_filename = f"{name}_template.txt"
            template_path = self.templates_dir / template_filename

            # Ensure templates directory exists
            self.templates_dir.mkdir(parents=True, exist_ok=True)

            # Write template file
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Clear cache
            if name in self._template_cache:
                del self._template_cache[name]

            return ServiceResult(success=True, data=str(template_path))

        except Exception as e:
            self.logger.error(f"Error creating custom template '{name}': {e}")
            return ServiceResult(
                success=False,
                error=f"Failed to create template: {str(e)}",
                error_code="TEMPLATE_CREATE_ERROR",
            )

    def _get_template_path(self, template_name: str) -> Optional[Path]:
        """
        Get the file path for a template.

        Args:
            template_name: Name of the template

        Returns:
            Path to the template file or None if not found
        """
        # Check if it's a default template
        if template_name in self.default_templates:
            template_file = self.default_templates[template_name]
            template_path = self.templates_dir / template_file
            if template_path.exists():
                return template_path

        # Check for custom template configuration
        if template_name == "prompt" and self.config.external_services.prompt_template:
            custom_path = Path(self.config.external_services.prompt_template)
            if custom_path.exists():
                return custom_path

        if (
            template_name == "enhancement"
            and self.config.external_services.enhancement_template
        ):
            custom_path = Path(self.config.external_services.enhancement_template)
            if custom_path.exists():
                return custom_path

        # Check for template file by name
        template_candidates = [
            self.templates_dir / f"{template_name}.txt",
            self.templates_dir / f"{template_name}_template.txt",
            Path(template_name) if os.path.isabs(template_name) else None,
        ]

        for candidate in template_candidates:
            if candidate and candidate.exists():
                return candidate

        return None

    def _substitute_variables(
        self, template_content: str, variables: Dict[str, Any]
    ) -> ServiceResult[str]:
        """
        Substitute variables in template content.

        Args:
            template_content: Template content with variables
            variables: Variable values for substitution

        Returns:
            ServiceResult containing the rendered content
        """
        try:
            # Convert all values to strings
            string_vars = {
                k: str(v) if v is not None else "" for k, v in variables.items()
            }

            # Add custom template variables from config
            custom_vars = self.config.external_services.custom_template_variables
            string_vars.update({k: str(v) for k, v in custom_vars.items()})

            # Use Python's Template class for safe substitution
            template = Template(template_content)

            try:
                # Perform substitution
                rendered = template.safe_substitute(**string_vars)

                # Check for unresolved variables
                unresolved = re.findall(r"\$\{([^}]+)\}", rendered)
                if unresolved:
                    self.logger.warning(f"Unresolved template variables: {unresolved}")

                return ServiceResult(success=True, data=rendered)

            except (KeyError, ValueError) as e:
                return ServiceResult(
                    success=False,
                    error=f"Variable substitution error: {str(e)}",
                    error_code="VARIABLE_SUBSTITUTION_ERROR",
                )

        except Exception as e:
            self.logger.error(f"Error in variable substitution: {e}")
            return ServiceResult(
                success=False,
                error=f"Variable substitution failed: {str(e)}",
                error_code="SUBSTITUTION_ERROR",
            )

    def _extract_template_variables(self, template_content: str) -> List[str]:
        """
        Extract variable names from template content.

        Args:
            template_content: Template content to analyze

        Returns:
            List of variable names found in template
        """
        # Find variables in format ${variable_name} and {variable_name}
        pattern = r"\$?\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
        matches = re.findall(pattern, template_content)

        # Remove duplicates and return sorted list
        return sorted(list(set(matches)))
