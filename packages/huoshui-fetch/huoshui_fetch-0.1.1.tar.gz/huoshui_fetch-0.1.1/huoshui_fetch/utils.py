"""Utility functions for huoshui-fetch."""

import re
from typing import Any
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Validates if a string is a valid URL.

    Args:
        url: String to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_url(url: str) -> str:
    """
    Sanitizes a URL by adding scheme if missing and cleaning whitespace.

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL
    """
    url = url.strip()

    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncates text to a maximum length, preserving word boundaries.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    # Find last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")

    if last_space > max_length * 0.8:  # If space is reasonably close to end
        truncated = truncated[:last_space]

    return truncated + suffix


def clean_whitespace(text: str) -> str:
    """
    Cleans excessive whitespace from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)

    # Replace multiple newlines with double newline
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text.strip()


def format_error_response(error: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Formats an error response in a consistent way.

    Args:
        error: Error message
        context: Optional context information

    Returns:
        Formatted error response
    """
    response = {"success": False, "error": error}

    if context:
        response["context"] = context

    return response


def format_success_response(data: Any, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Formats a success response in a consistent way.

    Args:
        data: Response data
        metadata: Optional metadata

    Returns:
        Formatted success response
    """
    response = {"success": True, "data": data}

    if metadata:
        response["metadata"] = metadata

    return response
