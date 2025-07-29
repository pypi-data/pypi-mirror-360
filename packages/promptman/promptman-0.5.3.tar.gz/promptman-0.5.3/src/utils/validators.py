"""
Common validation utilities for the AI Prompt Manager application.

This module provides reusable validation functions that can be used
throughout the application to ensure data consistency and security.
"""

import re
import unicodedata
from typing import List, Optional

try:
    from email.validator import EmailNotValidError
    from email.validator import validate_email as email_validator

    EMAIL_VALIDATOR_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATOR_AVAILABLE = False

from ..core.exceptions.base import ValidationException


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid

    Raises:
        ValidationException: If email is invalid
    """
    if not email or not isinstance(email, str):
        raise ValidationException("Email is required and must be a string")

    # Basic length check
    if len(email) > 254:  # RFC 5321 limit
        raise ValidationException("Email address is too long")

    if EMAIL_VALIDATOR_AVAILABLE:
        try:
            # Use email-validator library for comprehensive validation
            email_validator(email)
            return True
        except EmailNotValidError as e:
            raise ValidationException(f"Invalid email address: {str(e)}")
    else:
        # Fallback to regex if email-validator not available
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValidationException("Invalid email address format")
        return True


def validate_password(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digits: bool = True,
    require_special: bool = False,
    forbidden_passwords: Optional[List[str]] = None,
) -> bool:
    """
    Validate password strength.

    Args:
        password: Password to validate
        min_length: Minimum password length
        require_uppercase: Whether to require uppercase letters
        require_lowercase: Whether to require lowercase letters
        require_digits: Whether to require digits
        require_special: Whether to require special characters
        forbidden_passwords: List of forbidden passwords (e.g., common passwords)

    Returns:
        True if password is valid

    Raises:
        ValidationException: If password doesn't meet requirements
    """
    if not password or not isinstance(password, str):
        raise ValidationException("Password is required and must be a string")

    errors = []

    # Length check
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")

    # Maximum length check (prevent DoS)
    if len(password) > 128:
        errors.append("Password is too long (maximum 128 characters)")

    # Character requirements
    if require_uppercase and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if require_lowercase and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if require_digits and not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    # Common password check
    forbidden_list = forbidden_passwords or [
        "password",
        "123456",
        "password123",
        "admin",
        "qwerty",
        "letmein",
        "welcome",
        "monkey",
        "1234567890",
    ]

    if password.lower() in [p.lower() for p in forbidden_list]:
        errors.append("Password is too common and not allowed")

    # Sequential characters check
    if len(password) >= 3:
        for i in range(len(password) - 2):
            if (
                ord(password[i + 1]) == ord(password[i]) + 1
                and ord(password[i + 2]) == ord(password[i]) + 2
            ):
                errors.append("Password cannot contain sequential characters")
                break

    # Repeated characters check
    if len(set(password)) < len(password) * 0.5:  # More than 50% repeated characters
        errors.append("Password contains too many repeated characters")

    if errors:
        raise ValidationException("; ".join(errors))

    return True


def validate_prompt_name(name: str, max_length: int = 100) -> bool:
    """
    Validate prompt name format and constraints.

    Args:
        name: Prompt name to validate
        max_length: Maximum allowed length

    Returns:
        True if name is valid

    Raises:
        ValidationException: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValidationException("Prompt name is required and must be a string")

    # Remove leading/trailing whitespace
    name = name.strip()

    if not name:
        raise ValidationException("Prompt name cannot be empty or whitespace only")

    # Length checks
    if len(name) > max_length:
        raise ValidationException(
            f"Prompt name must be no more than {max_length} characters"
        )

    if len(name) < 2:
        raise ValidationException("Prompt name must be at least 2 characters long")

    # Character validation - allow letters, numbers, spaces, hyphens, underscores
    if not re.match(r"^[a-zA-Z0-9\s\-_]+$", name):
        raise ValidationException(
            "Prompt name can only contain letters, numbers, spaces, hyphens, and underscores"
        )

    # Cannot start or end with special characters
    if name[0] in "-_" or name[-1] in "-_":
        raise ValidationException(
            "Prompt name cannot start or end with hyphens or underscores"
        )

    # Cannot contain consecutive spaces
    if "  " in name:
        raise ValidationException("Prompt name cannot contain consecutive spaces")

    return True


def validate_string_length(
    text: Optional[str],
    field_name: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    allow_empty: bool = False,
) -> bool:
    """
    Validate string length constraints.

    Args:
        text: String to validate
        field_name: Name of the field for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        allow_empty: Whether to allow empty strings

    Returns:
        True if valid

    Raises:
        ValidationException: If validation fails
    """
    if text is None:
        if allow_empty:
            return True
        raise ValidationException(f"{field_name} is required")

    if not isinstance(text, str):
        raise ValidationException(f"{field_name} must be a string")

    if not allow_empty and not text.strip():
        raise ValidationException(f"{field_name} cannot be empty")

    if min_length is not None and len(text) < min_length:
        raise ValidationException(
            f"{field_name} must be at least {min_length} characters long"
        )

    if max_length is not None and len(text) > max_length:
        raise ValidationException(
            f"{field_name} must be no more than {max_length} characters long"
        )

    return True


def validate_uuid(uuid_string: str, field_name: str = "UUID") -> bool:
    """
    Validate UUID format.

    Args:
        uuid_string: UUID string to validate
        field_name: Name of the field for error messages

    Returns:
        True if valid UUID

    Raises:
        ValidationException: If UUID is invalid
    """
    if not uuid_string or not isinstance(uuid_string, str):
        raise ValidationException(f"{field_name} is required and must be a string")

    # UUID v4 pattern
    uuid_pattern = (
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )

    if not re.match(uuid_pattern, uuid_string.lower()):
        raise ValidationException(f"Invalid {field_name} format")

    return True


def validate_category(
    category: str, allowed_categories: Optional[List[str]] = None
) -> bool:
    """
    Validate category value.

    Args:
        category: Category to validate
        allowed_categories: List of allowed categories

    Returns:
        True if valid

    Raises:
        ValidationException: If category is invalid
    """
    if not category or not isinstance(category, str):
        raise ValidationException("Category is required and must be a string")

    category = category.strip()

    if not category:
        raise ValidationException("Category cannot be empty")

    # Default allowed categories if none provided
    if allowed_categories is None:
        allowed_categories = [
            "General",
            "Writing",
            "Analysis",
            "Code",
            "Creative",
            "Business",
            "Technical",
            "Research",
            "Education",
            "Other",
        ]

    if category not in allowed_categories:
        raise ValidationException(
            f"Invalid category '{category}'. Allowed categories: {', '.join(allowed_categories)}"
        )

    return True


def validate_tags(
    tags_string: str, max_tags: int = 10, max_tag_length: int = 30
) -> List[str]:
    """
    Validate and parse tags string.

    Args:
        tags_string: Comma-separated tags string
        max_tags: Maximum number of tags allowed
        max_tag_length: Maximum length per tag

    Returns:
        List of validated tags

    Raises:
        ValidationException: If tags are invalid
    """
    if not tags_string:
        return []

    if not isinstance(tags_string, str):
        raise ValidationException("Tags must be a string")

    # Split by comma and clean up
    tags = [tag.strip().lower() for tag in tags_string.split(",")]
    tags = [tag for tag in tags if tag]  # Remove empty tags

    if len(tags) > max_tags:
        raise ValidationException(f"Maximum {max_tags} tags allowed")

    # Validate each tag
    validated_tags = []
    for tag in tags:
        if len(tag) > max_tag_length:
            raise ValidationException(
                f"Tag '{tag}' is too long (max {max_tag_length} characters)"
            )

        if not re.match(r"^[a-zA-Z0-9\-_]+$", tag):
            raise ValidationException(f"Tag '{tag}' contains invalid characters")

        validated_tags.append(tag)

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in validated_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags


def validate_content_length(content: str, max_length: int = 50000) -> bool:
    """
    Validate content length for prompts and other text fields.

    Args:
        content: Content to validate
        max_length: Maximum allowed length

    Returns:
        True if valid

    Raises:
        ValidationException: If content is invalid
    """
    if not content or not isinstance(content, str):
        raise ValidationException("Content is required and must be a string")

    if not content.strip():
        raise ValidationException("Content cannot be empty")

    if len(content) > max_length:
        raise ValidationException(f"Content is too long (max {max_length} characters)")

    # Check for potentially malicious content
    suspicious_patterns = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>",  # Iframes
        r"<object[^>]*>",  # Object tags
        r"<embed[^>]*>",  # Embed tags
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            raise ValidationException("Content contains potentially unsafe elements")

    return True


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename
        max_length: Maximum allowed length

    Returns:
        Sanitized filename

    Raises:
        ValidationException: If filename cannot be sanitized
    """
    if not filename or not isinstance(filename, str):
        raise ValidationException("Filename is required and must be a string")

    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove or replace unsafe characters
    unsafe_chars = '<>:"|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")

    # Remove control characters
    filename = "".join(char for char in filename if ord(char) >= 32)

    # Normalize unicode
    filename = unicodedata.normalize("NFKD", filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    if not filename:
        raise ValidationException("Filename cannot be empty after sanitization")

    # Truncate if too long
    if len(filename) > max_length:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        max_name_length = max_length - len(ext) - 1 if ext else max_length
        filename = name[:max_name_length] + ("." + ext if ext else "")

    # Check for reserved names (Windows)
    reserved_names = [
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    ]

    name_without_ext = filename.split(".")[0].upper()
    if name_without_ext in reserved_names:
        filename = f"_{filename}"

    return filename


def validate_api_token_name(name: str) -> bool:
    """
    Validate API token name.

    Args:
        name: Token name to validate

    Returns:
        True if valid

    Raises:
        ValidationException: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValidationException("Token name is required and must be a string")

    name = name.strip()

    if not name:
        raise ValidationException("Token name cannot be empty")

    if len(name) > 50:
        raise ValidationException("Token name must be no more than 50 characters")

    if len(name) < 3:
        raise ValidationException("Token name must be at least 3 characters long")

    # Allow letters, numbers, spaces, hyphens, underscores
    if not re.match(r"^[a-zA-Z0-9\s\-_]+$", name):
        raise ValidationException(
            "Token name can only contain letters, numbers, spaces, hyphens, and underscores"
        )

    return True
