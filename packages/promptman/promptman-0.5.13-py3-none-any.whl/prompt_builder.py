"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Prompt Builder Service for AI Prompt Manager
Allows users to combine multiple existing prompts into new ones with drag-and-drop
interface

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from i18n import t


class PromptBuilder:
    """
    Service for building new prompts by combining existing ones
    Supports drag-and-drop reordering and template-based combination
    """

    def __init__(self):
        self.combination_templates = {
            "sequential": self._combine_sequential,
            "sections": self._combine_sections,
            "layered": self._combine_layered,
            "custom": self._combine_custom,
        }

    def get_available_prompts(self, data_manager) -> List[Dict]:
        """Get all available prompts for building"""
        if not data_manager:
            return []

        prompts = data_manager.get_all_prompts()

        # Format prompts for builder UI
        formatted_prompts = []
        for prompt in prompts:
            formatted_prompts.append(
                {
                    "id": prompt.get("id", str(uuid.uuid4())),
                    "name": prompt["name"],
                    "title": prompt["title"],
                    "category": prompt["category"],
                    "content": prompt["content"],
                    "tags": prompt.get("tags", ""),
                    "is_enhancement": prompt.get("is_enhancement_prompt", False),
                    "length": len(prompt["content"]),
                    "preview": self._generate_preview(prompt["content"]),
                    "created_at": prompt.get("created_at", datetime.now().isoformat()),
                }
            )

        return formatted_prompts

    def _generate_preview(self, content: str, max_length: int = 100) -> str:
        """Generate a preview of prompt content"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def get_combination_templates(self) -> Dict[str, Dict]:
        """Get available combination templates"""
        return {
            "sequential": {
                "name": t("builder.template.sequential"),
                "description": t("builder.template.sequential.desc"),
                "icon": "📋",
                "separator": "\n\n",
            },
            "sections": {
                "name": t("builder.template.sections"),
                "description": t("builder.template.sections.desc"),
                "icon": "📑",
                "separator": "\n\n---\n\n",
            },
            "layered": {
                "name": t("builder.template.layered"),
                "description": t("builder.template.layered.desc"),
                "icon": "🏗️",
                "separator": "\n\n",
            },
            "custom": {
                "name": t("builder.template.custom"),
                "description": t("builder.template.custom.desc"),
                "icon": "🎨",
                "separator": "",
            },
        }

    def combine_prompts(
        self,
        selected_prompts: List[Dict],
        template: str = "sequential",
        custom_options: Optional[Dict] = None,
    ) -> Tuple[bool, str, Dict]:
        """
        Combine selected prompts using specified template

        Args:
            selected_prompts: List of prompts in desired order
            template: Combination template to use
            custom_options: Additional options for custom template

        Returns:
            Tuple of (success, error_message, combined_prompt_data)
        """
        if not selected_prompts:
            return False, t("builder.error.no_prompts"), {}

        if len(selected_prompts) < 2:
            return False, t("builder.error.min_prompts"), {}

        try:
            if template not in self.combination_templates:
                template = "sequential"

            combine_function = self.combination_templates[template]
            combined_content = combine_function(selected_prompts, custom_options or {})

            # Generate metadata for combined prompt
            combined_prompt = {
                "content": combined_content,
                "source_prompts": [p["name"] for p in selected_prompts],
                "template_used": template,
                "combined_at": datetime.now().isoformat(),
                "total_length": len(combined_content),
                "source_count": len(selected_prompts),
                "suggested_name": self._generate_suggested_name(selected_prompts),
                "suggested_title": self._generate_suggested_title(selected_prompts),
                "suggested_category": self._determine_category(selected_prompts),
                "suggested_tags": self._generate_combined_tags(selected_prompts),
            }

            return True, "", combined_prompt

        except Exception as e:
            return False, f"{t('builder.error.combination')}: {str(e)}", {}

    def _combine_sequential(self, prompts: List[Dict], options: Dict) -> str:
        """Combine prompts sequentially with clear separation"""
        separator: str = options.get("separator", "\n\n")

        parts = []
        for i, prompt in enumerate(prompts, 1):
            if options.get("add_numbers", True):
                parts.append(f"{i}. {prompt['content']}")
            else:
                parts.append(prompt["content"])

        return separator.join(parts)

    def _combine_sections(self, prompts: List[Dict], options: Dict) -> str:
        """Combine prompts as distinct sections with headers"""
        parts = []

        for prompt in prompts:
            header = (
                f"## {prompt['title']}\n"
                if prompt.get("title")
                else f"## {prompt['name']}\n"
            )
            parts.append(header + prompt["content"])

        return "\n\n---\n\n".join(parts)

    def _combine_layered(self, prompts: List[Dict], options: Dict) -> str:
        """Combine prompts in layers with context building"""
        if not prompts:
            return ""

        # Start with base context from first prompt
        base_prompt = prompts[0]
        result = f"Base Context:\n{base_prompt['content']}\n\n"

        # Add layers
        for i, prompt in enumerate(prompts[1:], 1):
            result += f"Layer {i}:\n{prompt['content']}\n\n"

        # Add integration instruction
        result += "Instructions: Integrate all layers above into a cohesive response."

        return result

    def _combine_custom(self, prompts: List[Dict], options: Dict) -> str:
        """Combine prompts using custom template"""
        template: str = options.get("template", "{content}")
        separator: str = options.get("separator", "\n\n")

        formatted_prompts = []
        for prompt in prompts:
            # Replace placeholders in template
            formatted_content = template.format(
                content=prompt["content"],
                name=prompt["name"],
                title=prompt.get("title", ""),
                category=prompt.get("category", ""),
                tags=prompt.get("tags", ""),
            )
            formatted_prompts.append(formatted_content)

        return separator.join(formatted_prompts)

    def _generate_suggested_name(self, prompts: List[Dict]) -> str:
        """Generate a suggested name for the combined prompt"""
        if len(prompts) <= 3:
            names = [p["name"][:15] for p in prompts]
            return f"Combined_{'+'.join(names)}"
        else:
            return (
                f"Combined_{len(prompts)}_Prompts_{datetime.now().strftime('%Y%m%d')}"
            )

    def _generate_suggested_title(self, prompts: List[Dict]) -> str:
        """Generate a suggested title for the combined prompt"""
        categories = list(set(p.get("category", "General") for p in prompts))
        if len(categories) == 1:
            return f"Combined {categories[0]} Prompt"
        else:
            return f"Multi-Category Combined Prompt ({len(prompts)} parts)"

    def _determine_category(self, prompts: List[Dict]) -> str:
        """Determine the best category for the combined prompt"""
        categories = [p.get("category", "General") for p in prompts]

        # If all prompts are from the same category, use that
        if len(set(categories)) == 1:
            return str(categories[0])

        # Otherwise, use 'Combined' as category
        return "Combined"

    def _generate_combined_tags(self, prompts: List[Dict]) -> str:
        """Generate combined tags from all source prompts"""
        all_tags = []

        for prompt in prompts:
            tags = prompt.get("tags", "")
            if tags:
                # Split tags and clean them
                prompt_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
                all_tags.extend(prompt_tags)

        # Remove duplicates and sort
        unique_tags = sorted(list(set(all_tags)))

        # Add special tags
        unique_tags.append("combined")
        unique_tags.append(f"{len(prompts)}-part")

        return ", ".join(unique_tags)

    def validate_combination(self, selected_prompts: List[Dict]) -> Tuple[bool, str]:
        """Validate that the prompt combination is valid"""
        if not selected_prompts:
            return False, t("builder.error.no_prompts")

        if len(selected_prompts) < 2:
            return False, t("builder.error.min_prompts")

        # Check for duplicate prompts
        names = [p["name"] for p in selected_prompts]
        if len(names) != len(set(names)):
            return False, t("builder.error.duplicates")

        # Check total length
        total_length = sum(len(p["content"]) for p in selected_prompts)
        if total_length > 50000:  # 50K character limit
            return False, t("builder.error.too_long")

        return True, ""

    def get_combination_preview(
        self, selected_prompts: List[Dict], template: str = "sequential"
    ) -> str:
        """Generate a preview of what the combined prompt would look like"""
        if not selected_prompts:
            return t("builder.preview.empty")

        try:
            success, error, combined = self.combine_prompts(selected_prompts, template)
            if success:
                content = combined["content"]
                if len(content) > 500:
                    preview: str = (
                        content[:500]
                        + f"\n\n... ({len(content) - 500} more characters)"
                    )
                    return preview
                return str(content)
            else:
                return f"{t('builder.preview.error')}: {error}"
        except Exception as e:
            return f"{t('builder.preview.error')}: {str(e)}"


# Global prompt builder instance
prompt_builder = PromptBuilder()
