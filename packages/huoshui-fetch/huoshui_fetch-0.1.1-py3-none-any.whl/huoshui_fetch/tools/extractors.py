"""Data extraction tools for huoshui-fetch."""

import json
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from readability.readability import Document as Readability


def extract_article(html: str, url: str | None = None) -> dict[str, str]:
    """
    Extracts the main article content from a web page using readability.

    Args:
        html: HTML content
        url: Optional URL for resolving relative links

    Returns:
        Dictionary with title, content, and excerpt
    """
    if not html:
        return {"title": "", "content": "", "excerpt": "", "error": "No HTML content provided"}

    try:
        doc = Readability(html, url=url)
        article_html = doc.summary()
        article_title = doc.title()

        # Extract text content
        soup = BeautifulSoup(article_html, "lxml")
        text_content = soup.get_text(separator="\n", strip=True)

        # Create excerpt (first 200 chars)
        excerpt = text_content[:200] + "..." if len(text_content) > 200 else text_content

        return {
            "title": article_title or "",
            "content": article_html or "",
            "text_content": text_content,
            "excerpt": excerpt,
            "short_title": article_title.split(" - ")[0] if article_title else "",
        }
    except Exception as e:
        return {
            "title": "",
            "content": "",
            "excerpt": "",
            "error": f"Error extracting article: {str(e)}",
        }


def extract_links(
    html: str, base_url: str | None = None, internal_only: bool = False
) -> list[dict[str, str]]:
    """
    Extracts all links from HTML content.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative links
        internal_only: Only return links from the same domain

    Returns:
        List of dictionaries containing link information
    """
    if not html:
        return []

    try:
        soup = BeautifulSoup(html, "lxml")
        links = []
        base_domain = urlparse(base_url).netloc if base_url else None

        for link in soup.find_all("a", href=True):
            href = link["href"]

            # Resolve relative URLs
            if base_url:
                href = urljoin(base_url, href)

            # Skip if internal_only and link is external
            if internal_only and base_domain:
                link_domain = urlparse(href).netloc
                if link_domain != base_domain:
                    continue

            links.append(
                {
                    "url": href,
                    "text": link.get_text(strip=True),
                    "title": link.get("title", ""),
                    "rel": link.get("rel", []),
                }
            )

        return links
    except Exception as e:
        return [{"error": f"Error extracting links: {str(e)}"}]


def extract_metadata(html: str) -> dict[str, Any]:
    """
    Extracts metadata from HTML including title, description, and Open Graph tags.

    Args:
        html: HTML content

    Returns:
        Dictionary containing extracted metadata
    """
    if not html:
        return {"error": "No HTML content provided"}

    try:
        soup = BeautifulSoup(html, "lxml")
        metadata = {}

        # Basic metadata
        title_tag = soup.find("title")
        metadata["title"] = title_tag.get_text(strip=True) if title_tag else ""

        # Meta description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            metadata["description"] = desc_tag.get("content", "")

        # Keywords
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag:
            metadata["keywords"] = keywords_tag.get("content", "")

        # Author
        author_tag = soup.find("meta", attrs={"name": "author"})
        if author_tag:
            metadata["author"] = author_tag.get("content", "")

        # Open Graph tags
        og_tags = {}
        for tag in soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")}):
            property_name = tag.get("property", "").replace("og:", "")
            og_tags[property_name] = tag.get("content", "")

        if og_tags:
            metadata["open_graph"] = og_tags

        # Twitter Card tags
        twitter_tags = {}
        for tag in soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")}):
            property_name = tag.get("name", "").replace("twitter:", "")
            twitter_tags[property_name] = tag.get("content", "")

        if twitter_tags:
            metadata["twitter_card"] = twitter_tags

        # Canonical URL
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical:
            metadata["canonical_url"] = canonical.get("href", "")

        # Language
        html_tag = soup.find("html")
        if html_tag:
            metadata["language"] = html_tag.get("lang", "")

        return metadata
    except Exception as e:
        return {"error": f"Error extracting metadata: {str(e)}"}


def extract_images(
    html: str, base_url: str | None = None, min_size: dict[str, int] | None = None
) -> list[dict[str, Any]]:
    """
    Extracts all images from HTML content.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative image URLs
        min_size: Minimum size filter {"width": 100, "height": 100}

    Returns:
        List of image information dictionaries
    """
    if not html:
        return []

    try:
        soup = BeautifulSoup(html, "lxml")
        images = []

        for img in soup.find_all("img"):
            img_data = {
                "src": img.get("src", ""),
                "alt": img.get("alt", ""),
                "title": img.get("title", ""),
                "width": img.get("width", ""),
                "height": img.get("height", ""),
                "loading": img.get("loading", ""),
                "srcset": img.get("srcset", ""),
            }

            # Resolve relative URLs
            if base_url and img_data["src"]:
                img_data["src"] = urljoin(base_url, img_data["src"])

            # Apply size filter if specified
            if min_size:
                try:
                    width = int(img_data["width"]) if img_data["width"] else 0
                    height = int(img_data["height"]) if img_data["height"] else 0

                    if width < min_size.get("width", 0) or height < min_size.get("height", 0):
                        continue
                except ValueError:
                    pass

            images.append(img_data)

        return images
    except Exception as e:
        return [{"error": f"Error extracting images: {str(e)}"}]


def extract_structured_data(html: str) -> dict[str, Any]:
    """
    Extracts structured data (JSON-LD, microdata) from HTML.

    Args:
        html: HTML content

    Returns:
        Dictionary containing extracted structured data
    """
    if not html:
        return {"error": "No HTML content provided"}

    try:
        soup = BeautifulSoup(html, "lxml")
        structured_data = {}

        # Extract JSON-LD
        json_ld_scripts = soup.find_all("script", type="application/ld+json")
        if json_ld_scripts:
            json_ld_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    json_ld_data.append(data)
                except json.JSONDecodeError:
                    continue

            if json_ld_data:
                structured_data["json_ld"] = json_ld_data

        # Extract basic microdata (simplified)
        microdata_items = []
        for item in soup.find_all(attrs={"itemscope": True}):
            item_data = {"type": item.get("itemtype", ""), "properties": {}}

            # Find all properties within this item
            for prop in item.find_all(attrs={"itemprop": True}):
                prop_name = prop.get("itemprop")
                prop_value = prop.get("content") or prop.get_text(strip=True)

                if prop_name in item_data["properties"]:
                    # Convert to list if multiple values
                    if not isinstance(item_data["properties"][prop_name], list):
                        item_data["properties"][prop_name] = [item_data["properties"][prop_name]]
                    item_data["properties"][prop_name].append(prop_value)
                else:
                    item_data["properties"][prop_name] = prop_value

            if item_data["properties"]:
                microdata_items.append(item_data)

        if microdata_items:
            structured_data["microdata"] = microdata_items

        return structured_data if structured_data else {"message": "No structured data found"}
    except Exception as e:
        return {"error": f"Error extracting structured data: {str(e)}"}
