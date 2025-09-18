import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

from graph.utilities.bcolors import bcolors


def _is_localhost_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    host = parsed.hostname or ""
    return host in ("localhost", "127.0.0.1", "0.0.0.0")


@tool("localhost_scrape")
def localhost_scrape(url: str, max_chars: int = 1000000, timeout_seconds: float = 5.0) -> str:
    """Fetch and return visible text content from a localhost URL.

    Only allows hosts: localhost, 127.0.0.1, 0.0.0.0, ::1.
    """
    if not isinstance(url, str) or not url:
        return "error: url must be a non-empty string"

    if not _is_localhost_url(url):
        return "error: only localhost URLs are allowed"

    try:
        headers = {"User-Agent": "HoneycombLocalScraper/1.0"}
        response = requests.get(url, headers=headers, timeout=timeout_seconds, allow_redirects=True)
    except Exception as ex:
        print(f"{bcolors.FAIL}Local scrape request failed: {ex}{bcolors.ENDC}")
        return f"error: request failed: {ex}"

    if not (200 <= response.status_code < 300):
        return f"error: http status {response.status_code}"

    content_type = (response.headers.get("Content-Type") or "").lower()

    if "html" in content_type or "<html" in response.text[:200].lower():
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
    else:
        text = response.text

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    text = text.strip()

    if not text:
        return "error: no extractable text content"

    if len(text) > max_chars:
        return "error: text is too long"

    return text


