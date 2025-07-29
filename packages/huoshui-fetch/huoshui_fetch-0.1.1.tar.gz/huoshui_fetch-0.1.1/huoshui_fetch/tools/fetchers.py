"""Web fetching tools for huoshui-fetch."""

import asyncio

import httpx
from pydantic import BaseModel


class FetchResult(BaseModel):
    """Result of a fetch operation."""

    url: str
    status_code: int
    content: str
    headers: dict[str, str]
    encoding: str | None = None
    error: str | None = None


async def fetch_url(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    follow_redirects: bool = True,
    user_agent: str | None = None,
) -> FetchResult:
    """
    Fetches content from a URL with customizable options.

    Args:
        url: The URL to fetch
        headers: Optional custom headers
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow redirects
        user_agent: Custom user agent string

    Returns:
        FetchResult containing the response data
    """
    default_headers = {
        "User-Agent": user_agent
        or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    if headers:
        default_headers.update(headers)

    try:
        async with httpx.AsyncClient(follow_redirects=follow_redirects) as client:
            response = await client.get(url, headers=default_headers, timeout=timeout)

            return FetchResult(
                url=str(response.url),
                status_code=response.status_code,
                content=response.text,
                headers=dict(response.headers),
                encoding=response.encoding,
            )
    except httpx.TimeoutException:
        return FetchResult(
            url=url,
            status_code=0,
            content="",
            headers={},
            error=f"Request timed out after {timeout} seconds",
        )
    except httpx.RequestError as e:
        return FetchResult(
            url=url, status_code=0, content="", headers={}, error=f"Request failed: {str(e)}"
        )
    except Exception as e:
        return FetchResult(
            url=url, status_code=0, content="", headers={}, error=f"Unexpected error: {str(e)}"
        )


async def fetch_with_headers(
    url: str, custom_headers: dict[str, str], timeout: float = 30.0
) -> FetchResult:
    """
    Fetches a URL with custom headers.

    Args:
        url: The URL to fetch
        custom_headers: Dictionary of custom headers
        timeout: Request timeout in seconds

    Returns:
        FetchResult containing the response data
    """
    return await fetch_url(url, headers=custom_headers, timeout=timeout)


