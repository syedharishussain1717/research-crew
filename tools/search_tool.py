"""Real web search tool (DuckDuckGo via the `ddgs` package).

Every result the agent sees is also saved in SEARCH_LOG, so the app can show
the REAL sources that were found, never sources invented by the AI.
"""
from crewai.tools import tool
from ddgs import DDGS

# Filled during a run, read by the UI afterwards.
SEARCH_LOG: list[dict] = []


def reset_search_log() -> None:
    SEARCH_LOG.clear()


def get_unique_sources() -> list[dict]:
    """Return every distinct URL found during the run."""
    seen, sources = set(), []
    for item in SEARCH_LOG:
        if item["url"] and item["url"] not in seen:
            seen.add(item["url"])
            sources.append(item)
    return sources


@tool("search_web")
def search_web(query: str) -> str:
    """Search the web for a query. Returns titles, URLs and short snippets."""
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as error:  # network problem, rate limit, etc.
        return f"SEARCH FAILED for '{query}': {error}. Try a different query."

    if not results:
        return f"No results found for '{query}'. Try different keywords."

    lines = []
    for r in results:
        title = (r.get("title") or "").strip()
        url = (r.get("href") or "").strip()
        snippet = (r.get("body") or "").strip()[:300]
        SEARCH_LOG.append({"query": query, "title": title, "url": url, "snippet": snippet})
        lines.append(f"TITLE: {title}\nURL: {url}\nSNIPPET: {snippet}")
    return "\n\n".join(lines)