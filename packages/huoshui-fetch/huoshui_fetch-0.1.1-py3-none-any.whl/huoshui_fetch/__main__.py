import json
from typing import Any

from fastmcp import FastMCP

from .tools.converters import clean_html, html_to_markdown, html_to_text, json_to_markdown
from .tools.extractors import (
    extract_article,
    extract_images,
    extract_links,
    extract_metadata,
    extract_structured_data,
)

# Import tools from modules
from .tools.fetchers import fetch_url as async_fetch_url, fetch_with_headers as async_fetch_with_headers
from .utils import format_error_response, format_success_response, is_valid_url, sanitize_url

# Create the FastMCP server
mcp = FastMCP(
    name="huoshui-fetch",
    instructions="""Web content fetching and conversion MCP server.

This server provides tools for:
- Fetching web content with customizable options
- Converting HTML to various formats (Markdown, plain text)
- Extracting structured data from web pages
- Parsing articles, links, metadata, and images

All tools use STDIO transport for local operation.""",
)


# Fetching tools
@mcp.tool
async def fetch_url(
    url: str, timeout: float = 30.0, follow_redirects: bool = True, user_agent: str | None = None
) -> dict[str, Any]:
    """
    Fetches content from a URL.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds (default: 30)
        follow_redirects: Whether to follow redirects (default: True)
        user_agent: Custom user agent string (optional)

    Returns:
        Dictionary containing status_code, content, headers, encoding, and error (if any)
    """
    if not is_valid_url(url):
        url = sanitize_url(url)
        if not is_valid_url(url):
            return format_error_response(f"Invalid URL: {url}")

    result = await async_fetch_url(
        url=url, timeout=timeout, follow_redirects=follow_redirects, user_agent=user_agent
    )

    if result.error:
        return format_error_response(result.error, {"url": url})

    return format_success_response(
        {
            "url": result.url,
            "status_code": result.status_code,
            "content": result.content,
            "headers": result.headers,
            "encoding": result.encoding,
        }
    )


@mcp.tool
async def fetch_with_headers(url: str, headers: dict[str, str], timeout: float = 30.0) -> dict[str, Any]:
    """
    Fetches a URL with custom headers.

    Args:
        url: The URL to fetch
        headers: Dictionary of custom headers
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Dictionary containing status_code, content, headers, encoding, and error (if any)
    """
    if not is_valid_url(url):
        url = sanitize_url(url)
        if not is_valid_url(url):
            return format_error_response(f"Invalid URL: {url}")

    result = await async_fetch_with_headers(url=url, custom_headers=headers, timeout=timeout)

    if result.error:
        return format_error_response(result.error, {"url": url})

    return format_success_response(
        {
            "url": result.url,
            "status_code": result.status_code,
            "content": result.content,
            "headers": result.headers,
            "encoding": result.encoding,
        }
    )


# Conversion tools
@mcp.tool
def html_to_markdown_tool(
    html: str, strip_tags: list[str] | None = None, heading_style: str = "ATX"
) -> dict[str, Any]:
    """
    Converts HTML content to Markdown format.

    Args:
        html: HTML content to convert
        strip_tags: List of tags to strip (default: ['script', 'style', 'meta', 'link'])
        heading_style: Style for headings - "ATX" or "SETEXT" (default: "ATX")

    Returns:
        Dictionary with converted markdown content
    """
    try:
        markdown = html_to_markdown(html, strip_tags=strip_tags, heading_style=heading_style)
        return format_success_response({"markdown": markdown})
    except Exception as e:
        return format_error_response(str(e))


@mcp.tool
def html_to_text_tool(html: str, preserve_links: bool = False) -> dict[str, Any]:
    """
    Extracts plain text from HTML content.

    Args:
        html: HTML content to convert
        preserve_links: Whether to preserve link URLs in output (default: False)

    Returns:
        Dictionary with extracted text
    """
    try:
        text = html_to_text(html, preserve_links=preserve_links)
        return format_success_response({"text": text})
    except Exception as e:
        return format_error_response(str(e))


@mcp.tool
def clean_html_tool(html: str, allowed_tags: list[str] | None = None) -> dict[str, Any]:
    """
    Cleans HTML by removing scripts, styles, and optionally limiting to allowed tags.

    Args:
        html: HTML content to clean
        allowed_tags: List of allowed tags (None = all tags except script/style)

    Returns:
        Dictionary with cleaned HTML
    """
    try:
        cleaned = clean_html(html, allowed_tags=allowed_tags)
        return format_success_response({"html": cleaned})
    except Exception as e:
        return format_error_response(str(e))


# Extraction tools
@mcp.tool
def extract_article_tool(html: str, url: str | None = None) -> dict[str, Any]:
    """
    Extracts the main article content from a web page.

    Args:
        html: HTML content
        url: Optional URL for resolving relative links

    Returns:
        Dictionary with title, content, text_content, excerpt, and short_title
    """
    result = extract_article(html, url=url)
    if "error" in result:
        return format_error_response(result["error"])
    return format_success_response(result)


@mcp.tool
def extract_links_tool(
    html: str, base_url: str | None = None, internal_only: bool = False
) -> dict[str, Any]:
    """
    Extracts all links from HTML content.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
        internal_only: Only return links from the same domain (default: False)

    Returns:
        Dictionary with list of links containing url, text, title, and rel attributes
    """
    links = extract_links(html, base_url=base_url, internal_only=internal_only)
    if links and "error" in links[0]:
        return format_error_response(links[0]["error"])
    return format_success_response({"links": links, "count": len(links)})


@mcp.tool
def extract_metadata_tool(html: str) -> dict[str, Any]:
    """
    Extracts metadata from HTML including title, description, and Open Graph tags.

    Args:
        html: HTML content

    Returns:
        Dictionary containing title, description, keywords, author, open_graph, twitter_card, etc.
    """
    metadata = extract_metadata(html)
    if "error" in metadata:
        return format_error_response(metadata["error"])
    return format_success_response(metadata)


@mcp.tool
def extract_images_tool(
    html: str,
    base_url: str | None = None,
    min_width: int | None = None,
    min_height: int | None = None,
) -> dict[str, Any]:
    """
    Extracts all images from HTML content.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative image URLs
        min_width: Minimum image width filter
        min_height: Minimum image height filter

    Returns:
        Dictionary with list of images containing src, alt, title, dimensions, etc.
    """
    min_size = {}
    if min_width:
        min_size["width"] = min_width
    if min_height:
        min_size["height"] = min_height

    images = extract_images(html, base_url=base_url, min_size=min_size if min_size else None)
    if images and "error" in images[0]:
        return format_error_response(images[0]["error"])
    return format_success_response({"images": images, "count": len(images)})


@mcp.tool
def extract_structured_data_tool(html: str) -> dict[str, Any]:
    """
    Extracts structured data (JSON-LD, microdata) from HTML.

    Args:
        html: HTML content

    Returns:
        Dictionary containing json_ld and microdata if found
    """
    data = extract_structured_data(html)
    if "error" in data:
        return format_error_response(data["error"])
    return format_success_response(data)


# Utility tool for converting JSON to Markdown
@mcp.tool
def json_to_markdown_tool(json_data: str) -> dict[str, Any]:
    """
    Converts JSON data to readable Markdown format.

    Args:
        json_data: JSON string to convert

    Returns:
        Dictionary with markdown representation of the JSON
    """
    try:
        data = json.loads(json_data)
        markdown = json_to_markdown(data)
        return format_success_response({"markdown": markdown})
    except json.JSONDecodeError as e:
        return format_error_response(f"Invalid JSON: {str(e)}")
    except Exception as e:
        return format_error_response(str(e))


# Entry point for uvx
def main():
    """Main entry point for the huoshui-fetch MCP server."""
    mcp.run()


# Run the server with STDIO transport (default)
if __name__ == "__main__":
    main()
