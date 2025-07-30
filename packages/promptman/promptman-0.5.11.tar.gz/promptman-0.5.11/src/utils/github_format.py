"""
GitHub format utility for AI Prompt Manager.

This module provides utilities for importing and exporting prompts
in GitHub YAML format, supporting the standard GitHub prompt format.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..prompts.models.prompt import Prompt


class GitHubFormatHandler:
    """Handler for GitHub format prompt files."""

    def __init__(self):
        """Initialize the GitHub format handler."""
        self.supported_extensions = {".yml", ".yaml"}
        self.default_model = "openai/gpt-4o"

    def is_github_format(self, file_path: str) -> bool:
        """
        Check if a file is in GitHub format.

        Args:
            file_path: Path to the file

        Returns:
            True if file appears to be in GitHub format
        """
        if not Path(file_path).suffix.lower() in self.supported_extensions:
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                data = yaml.safe_load(content)

            # Check for GitHub format structure
            return (
                isinstance(data, dict)
                and "messages" in data
                and isinstance(data["messages"], list)
            )
        except (yaml.YAMLError, IOError, KeyError):
            return False

    def validate_github_format(self, data: Any) -> Tuple[bool, str]:
        """
        Validate GitHub format data structure.

        Args:
            data: Dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"

        if "messages" not in data:
            return False, "Missing required 'messages' field"

        if not isinstance(data["messages"], list):
            return False, "'messages' must be a list"

        if not data["messages"]:
            return False, "'messages' cannot be empty"

        # Validate each message
        for i, message in enumerate(data["messages"]):
            if not isinstance(message, dict):
                return False, f"Message {i} must be a dictionary"

            if "role" not in message:
                return False, f"Message {i} missing required 'role' field"

            if "content" not in message:
                return False, f"Message {i} missing required 'content' field"

            role = message["role"]
            if role not in ["system", "user", "assistant"]:
                return False, f"Message {i} has invalid role: {role}"

        # Validate optional fields
        if "model" in data and not isinstance(data["model"], str):
            return False, "'model' must be a string"

        numeric_fields = [
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
        ]
        for field in numeric_fields:
            if field in data and not isinstance(data[field], (int, float)):
                return False, f"'{field}' must be a number"

        return True, ""

    def import_from_file(
        self,
        file_path: str,
        tenant_id: str,
        user_id: str,
        name: Optional[str] = None,
        category: str = "GitHub Import",
    ) -> Prompt:
        """
        Import a prompt from a GitHub format file.

        Args:
            file_path: Path to the GitHub format file
            tenant_id: Tenant ID to assign
            user_id: User ID to assign
            name: Optional name for the prompt
            category: Category for the prompt

        Returns:
            Prompt instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            data = yaml.safe_load(content)

            # Validate format
            is_valid, error_msg = self.validate_github_format(data)
            if not is_valid:
                raise ValueError(f"Invalid GitHub format: {error_msg}")

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except IOError as e:
            raise ValueError(f"Error reading file: {e}")

        # Generate name from filename if not provided
        if not name:
            name = Path(file_path).stem
            # Clean up filename for use as name
            name = re.sub(r"[^a-zA-Z0-9\s\-_]", "", name)
            name = re.sub(r"\s+", " ", name).strip()
            if not name:
                name = "GitHub Import"

        return Prompt.from_github_format(
            data, tenant_id, user_id, name, category=category
        )

    def export_to_file(self, prompt: Prompt, file_path: str) -> None:
        """
        Export a prompt to a GitHub format file.

        Args:
            prompt: Prompt to export
            file_path: Output file path

        Raises:
            IOError: If file cannot be written
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            yaml_content = prompt.to_github_yaml()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml_content)

        except IOError as e:
            raise IOError(f"Error writing file: {e}")

    def import_from_directory(
        self,
        directory_path: str,
        tenant_id: str,
        user_id: str,
        category: str = "GitHub Import",
    ) -> List[Prompt]:
        """
        Import all GitHub format files from a directory.

        Args:
            directory_path: Path to directory containing GitHub files
            tenant_id: Tenant ID to assign
            user_id: User ID to assign
            category: Category for imported prompts

        Returns:
            List of imported Prompt instances
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        prompts = []
        directory = Path(directory_path)

        for file_path in directory.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_extensions
                and self.is_github_format(str(file_path))
            ):

                try:
                    prompt = self.import_from_file(
                        str(file_path), tenant_id, user_id, category=category
                    )
                    prompts.append(prompt)
                except (ValueError, FileNotFoundError) as e:
                    # Log error but continue with other files
                    print(f"Warning: Could not import {file_path}: {e}")

        return prompts

    def export_to_directory(
        self, prompts: List[Prompt], directory_path: str, use_prompt_names: bool = True
    ) -> List[str]:
        """
        Export prompts to GitHub format files in a directory.

        Args:
            prompts: List of prompts to export
            directory_path: Output directory path
            use_prompt_names: Whether to use prompt names as filenames

        Returns:
            List of created file paths
        """
        os.makedirs(directory_path, exist_ok=True)
        created_files = []

        for i, prompt in enumerate(prompts):
            if use_prompt_names:
                # Clean prompt name for filename
                filename = re.sub(r"[^a-zA-Z0-9\s\-_]", "", prompt.name)
                filename = re.sub(r"\s+", "_", filename).strip()
                if not filename:
                    filename = f"prompt_{i}"
            else:
                filename = f"prompt_{i}"

            filename = f"{filename}.yml"
            file_path = os.path.join(directory_path, filename)

            # Handle duplicate filenames
            counter = 1
            base_path = file_path
            while os.path.exists(file_path):
                name_part = Path(base_path).stem
                extension = Path(base_path).suffix
                file_path = os.path.join(
                    directory_path, f"{name_part}_{counter}{extension}"
                )
                counter += 1

            try:
                self.export_to_file(prompt, file_path)
                created_files.append(file_path)
            except IOError as e:
                print(f"Warning: Could not export {prompt.name}: {e}")

        return created_files

    def convert_content_to_github_format(self, content: str) -> Dict[str, Any]:
        """
        Convert plain text content to GitHub format structure.

        Args:
            content: Plain text content

        Returns:
            Dictionary in GitHub format
        """
        # Create a simple user message format
        return {
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": content},
            ],
            "model": self.default_model,
        }

    def get_format_info(self) -> Dict[str, Any]:
        """
        Get information about the GitHub format.

        Returns:
            Dictionary with format information
        """
        return {
            "name": "GitHub YAML Format",
            "description": "GitHub's standard YAML format for AI prompts",
            "extensions": list(self.supported_extensions),
            "required_fields": ["messages"],
            "optional_fields": [
                "model",
                "temperature",
                "max_tokens",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
            ],
            "message_roles": ["system", "user", "assistant"],
            "example": {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, how are you?"},
                ],
                "model": "openai/gpt-4o",
            },
        }
