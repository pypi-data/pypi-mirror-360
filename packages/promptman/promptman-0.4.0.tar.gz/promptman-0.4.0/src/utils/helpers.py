"""
General utility helper functions for the AI Prompt Manager application.

This module provides common utility functions that can be used throughout
the application for string manipulation, data formatting, and other tasks.
"""

import hashlib
import re
import secrets
import string
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def generate_uuid() -> str:
    """
    Generate a new UUID4 string.

    Returns:
        UUID4 string in lowercase
    """
    return str(uuid.uuid4())


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Length of the token (default: 32)

    Returns:
        URL-safe random token
    """
    return secrets.token_urlsafe(length)


def generate_api_token() -> Tuple[str, str, str]:
    """
    Generate an API token with prefix and hash.

    Returns:
        Tuple of (full_token, token_prefix, token_hash)
    """
    # Generate random token
    token_secret = secrets.token_urlsafe(32)

    # Create token with prefix
    full_token = f"apm_{token_secret}"

    # Create prefix for identification (first 8 chars after prefix)
    token_prefix = f"apm_{token_secret[:8]}"

    # Create hash for storage
    token_hash = hash_string(full_token)

    return full_token, token_prefix, token_hash


def hash_string(text: str) -> str:
    """
    Create a SHA-256 hash of a string.

    Args:
        text: String to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2 with SHA-256.

    Args:
        password: Password to hash
        salt: Optional salt (generates new one if not provided)

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt_str = secrets.token_hex(32)
        salt_bytes = salt_str.encode("utf-8")
    else:
        salt_str = salt
        salt_bytes = salt.encode("utf-8")

    # Use PBKDF2 with 100,000 iterations
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        100000,
    )

    return hashed.hex(), salt_str


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password
        hashed_password: Stored password hash
        salt: Password salt

    Returns:
        True if password matches
    """
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed_password


def sanitize_string(text: Any, max_length: Optional[int] = None) -> str:
    """
    Sanitize a string by removing potentially harmful content.

    Args:
        text: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)

    # Remove HTML/XML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove script content
    text = re.sub(
        r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL
    )

    # Replace HTML entities
    html_entities = {
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&quot;": '"',
        "&#x27;": "'",
        "&#x2F;": "/",
        "&#39;": "'",
    }

    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Remove control characters except newlines and tabs
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

    # Normalize whitespace
    text = " ".join(text.split())

    # Truncate if necessary
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip()

    return str(text)


def format_timestamp(
    dt: Optional[datetime] = None, include_timezone: bool = True
) -> str:
    """
    Format a datetime object as an ISO string.

    Args:
        dt: Datetime object (uses current time if None)
        include_timezone: Whether to include timezone info

    Returns:
        ISO formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()

    if include_timezone and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse an ISO timestamp string to datetime object.

    Args:
        timestamp_str: ISO timestamp string

    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        try:
            # Fallback for older format
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length with optional suffix.

    Args:
        text: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    if len(suffix) >= max_length:
        return text[:max_length]

    return text[: max_length - len(suffix)] + suffix


def slugify(text: str, max_length: int = 50) -> str:
    """
    Convert a string to a URL-friendly slug.

    Args:
        text: String to slugify
        max_length: Maximum slug length

    Returns:
        URL-friendly slug
    """
    # Convert to lowercase and remove special characters
    slug = re.sub(r"[^\w\s-]", "", text.lower())

    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r"[-\s]+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    return slug


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from a string.

    Args:
        text: String to extract numbers from

    Returns:
        List of extracted numbers
    """
    # Pattern matches integers and floats, including negative numbers
    pattern = r"-?\d+\.?\d*"
    matches = re.findall(pattern, text)

    numbers = []
    for match in matches:
        try:
            if "." in match:
                numbers.append(float(match))
            else:
                numbers.append(int(match))
        except ValueError:
            continue

    return numbers


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple similarity between two texts using character overlap.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0

    # Convert to lowercase and create character sets
    set1 = set(text1.lower())
    set2 = set(text2.lower())

    # Calculate Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union > 0 else 0.0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i : i + chunk_size])
    return chunks


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def escape_sql_like(text: str) -> str:
    """
    Escape special characters for SQL LIKE queries.

    Args:
        text: Text to escape

    Returns:
        Escaped text safe for LIKE queries
    """
    # Escape SQL LIKE wildcards
    text = text.replace("\\", "\\\\")  # Escape backslashes first
    text = text.replace("%", "\\%")  # Escape percent signs
    text = text.replace("_", "\\_")  # Escape underscores

    return text


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.

    Args:
        text: Text to search for URLs

    Returns:
        List of extracted URLs
    """
    url_pattern = r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w.))?)?"
    return re.findall(url_pattern, text)


def mask_sensitive_data(text: str, mask_char: str = "*") -> str:
    """
    Mask sensitive data in text (emails, phone numbers, etc.).

    Args:
        text: Text containing sensitive data
        mask_char: Character to use for masking

    Returns:
        Text with sensitive data masked
    """
    # Mask email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        lambda m: m.group(0)[:2] + mask_char * (len(m.group(0)) - 4) + m.group(0)[-2:],
        text,
    )

    # Mask phone numbers (simple pattern)
    text = re.sub(
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", lambda m: mask_char * len(m.group(0)), text
    )

    # Mask credit card numbers (simple pattern)
    text = re.sub(
        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        lambda m: mask_char * len(m.group(0)),
        text,
    )

    return text


def validate_json_structure(data: Any, required_keys: List[str]) -> bool:
    """
    Validate that a dictionary has required keys.

    Args:
        data: Dictionary to validate
        required_keys: List of required keys

    Returns:
        True if all required keys are present
    """
    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def rate_limit_key(identifier: str, window: str = "hour") -> str:
    """
    Generate a rate limiting key.

    Args:
        identifier: Unique identifier (user ID, IP, etc.)
        window: Time window (minute, hour, day)

    Returns:
        Rate limiting key
    """
    now = datetime.utcnow()

    if window == "minute":
        time_key = now.strftime("%Y%m%d%H%M")
    elif window == "hour":
        time_key = now.strftime("%Y%m%d%H")
    elif window == "day":
        time_key = now.strftime("%Y%m%d")
    else:
        time_key = now.strftime("%Y%m%d%H")

    return f"rate_limit:{identifier}:{window}:{time_key}"


def generate_password(
    length: int = 12,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_special: bool = True,
) -> str:
    """
    Generate a random password with specified constraints.

    Args:
        length: Password length
        include_uppercase: Include uppercase letters
        include_lowercase: Include lowercase letters
        include_digits: Include digits
        include_special: Include special characters

    Returns:
        Generated password
    """
    characters = ""

    if include_lowercase:
        characters += string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_digits:
        characters += string.digits
    if include_special:
        characters += "!@#$%^&*"

    if not characters:
        raise ValueError("At least one character type must be included")

    return "".join(secrets.choice(characters) for _ in range(length))
