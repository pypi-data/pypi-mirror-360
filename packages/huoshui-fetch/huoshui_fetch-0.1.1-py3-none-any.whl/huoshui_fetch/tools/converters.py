"""Content conversion tools for huoshui-fetch."""

from typing import Any

from bs4 import BeautifulSoup
from markdownify import markdownify as md


def html_to_markdown(
    html: str,
    strip_tags: list | None = None,
    heading_style: str = "ATX",
    bullets: str = "*",
    code_language: str = "",
    escape_asterisks: bool = True,
    escape_underscores: bool = True,
) -> str:
    """
    Converts HTML content to Markdown format.

    Args:
        html: HTML content to convert
        strip_tags: List of tags to strip from output
        heading_style: Style for headings ("ATX" or "SETEXT")
        bullets: Character to use for bullets
        code_language: Default language for code blocks
        escape_asterisks: Whether to escape asterisks
        escape_underscores: Whether to escape underscores

    Returns:
        Markdown formatted text
    """
    if not html:
        return ""

    strip_tags = strip_tags or ["script", "style", "meta", "link"]

    try:
        return md(
            html,
            heading_style=heading_style,
            bullets=bullets,
            code_language=code_language,
            escape_asterisks=escape_asterisks,
            escape_underscores=escape_underscores,
            strip=strip_tags,
        ).strip()
    except Exception as e:
        return f"Error converting HTML to Markdown: {str(e)}"


def html_to_text(html: str, preserve_links: bool = False) -> str:
    """
    Extracts plain text from HTML content.

    Args:
        html: HTML content to convert
        preserve_links: Whether to preserve link URLs in output

    Returns:
        Plain text extracted from HTML
    """
    if not html:
        return ""

    try:
        soup = BeautifulSoup(html, "lxml")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        if preserve_links:
            # Replace links with text [url]
            for link in soup.find_all("a", href=True):
                link.string = f"{link.get_text()} [{link['href']}]"

        # Get text and clean up whitespace
        text = soup.get_text(separator=" ", strip=True)

        # Clean up multiple spaces and newlines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        return f"Error extracting text from HTML: {str(e)}"


def clean_html(html: str, allowed_tags: list | None = None) -> str:
    """
    Cleans HTML by removing scripts, styles, and optionally limiting to allowed tags.

    Args:
        html: HTML content to clean
        allowed_tags: List of allowed tags (None = all tags except script/style)

    Returns:
        Cleaned HTML
    """
    if not html:
        return ""

    try:
        soup = BeautifulSoup(html, "lxml")

        # Always remove these tags
        for tag in soup(["script", "style", "meta", "link", "noscript"]):
            tag.decompose()

        # Remove comments
        for comment in soup.find_all(
            string=lambda text: isinstance(text, type(soup.new_string("")))
        ):
            if "<!--" in str(comment):
                comment.extract()

        # If allowed_tags is specified, remove all other tags
        if allowed_tags:
            for tag in soup.find_all():
                if tag.name not in allowed_tags:
                    tag.unwrap()

        return str(soup).strip()
    except Exception as e:
        return f"Error cleaning HTML: {str(e)}"


def json_to_markdown(data: Any, indent: int = 0) -> str:
    """
    Converts JSON data to readable Markdown format.

    Args:
        data: JSON data (dict, list, or primitive)
        indent: Current indentation level

    Returns:
        Markdown formatted representation of JSON
    """

    def _indent_text(text: str, level: int) -> str:
        return "  " * level + text

    if isinstance(data, dict):
        if not data:
            return _indent_text("*(empty object)*", indent)

        lines = []
        for key, value in data.items():
            if isinstance(value, dict | list):
                lines.append(_indent_text(f"**{key}:**", indent))
                lines.append(json_to_markdown(value, indent + 1))
            else:
                lines.append(_indent_text(f"**{key}:** {value}", indent))
        return "\n".join(lines)

    elif isinstance(data, list):
        if not data:
            return _indent_text("*(empty list)*", indent)

        lines = []
        for i, item in enumerate(data):
            if isinstance(item, dict | list):
                lines.append(_indent_text(f"- Item {i + 1}:", indent))
                lines.append(json_to_markdown(item, indent + 1))
            else:
                lines.append(_indent_text(f"- {item}", indent))
        return "\n".join(lines)

    else:
        return _indent_text(str(data), indent)
