"""Real web tools for Pooh, guarded by the interceptor + honeypot pipeline.

Both tools hit the real internet, then run their result through:
  1. maybe_inject()    -- the malicious-internet simulator (the threat)
  2. screen_and_wrap() -- the honeypot (the defense)

so Pooh only ever receives content that has been screened.
"""

import re

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from graph.interceptor import maybe_inject
from graph.honeypot import screen, is_url_banned


_tavily = TavilySearch(max_results=3)


def _guard(content: str, source: str, url: str | None = None) -> str:
    """Run freshly fetched web content through the threat + defense pipeline."""
    poisoned, _payload = maybe_inject(content, source=source)
    return screen(poisoned, source=source, url=url)


def _stringify_search(raw) -> str:
    """Flatten Tavily's result payload into plain text."""
    if isinstance(raw, dict) and isinstance(raw.get("results"), list):
        parts = []
        for r in raw["results"]:
            parts.append(
                f"Title: {r.get('title', '')}\n"
                f"URL: {r.get('url', '')}\n"
                f"{r.get('content', '')}"
            )
        if parts:
            return "\n\n".join(parts)
    return str(raw)


@tool("web_search")
def web_search(query: str) -> str:
    """Search the real web for up-to-date information about `query`."""
    raw = _tavily.invoke({"query": query})
    return _guard(_stringify_search(raw), source="web search results")


@tool("fetch_url")
def fetch_url(url: str, max_chars: int = 6000, timeout_seconds: float = 10.0) -> str:
    """Fetch a real web page by URL and return its visible text content."""
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return "error: url must start with http:// or https://"

    if is_url_banned(url):
        return (
            f"BLOCKED: {url} was previously flagged as a prompt-injection source "
            f"and is banned for this session. Do not retry it."
        )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PoohBot/1.0)"},
            timeout=timeout_seconds,
            allow_redirects=True,
        )
    except Exception as ex:
        return f"error: request failed: {ex}"

    if not (200 <= response.status_code < 300):
        return f"error: http status {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()

    if not text:
        return "error: no extractable text content"
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[truncated]"

    return _guard(text, source=f"page {url}", url=url)
