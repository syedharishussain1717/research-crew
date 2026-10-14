
from io import BytesIO
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from crewai.tools import tool
from pypdf import PdfReader

from tools.search_tool import SEARCH_LOG


@tool("open_file")
def open_file(path: str) -> str:
    """
    Read a webpage or PDF using a URL returned by search_web.
    The path argument must contain the exact HTTPS URL.
    """
    allowed_urls = {
        item["url"]
        for item in SEARCH_LOG
        if item.get("url")
    }

    if path not in allowed_urls:
        return "URL not found in search results. Use search_web first."

    parsed = urlparse(path)
    if parsed.scheme != "https" or not parsed.hostname:
        return "Only valid HTTPS URLs are supported."

    try:
        # Resolve the host and reject private/internal IP addresses.
        import ipaddress
        import socket

        addresses = socket.getaddrinfo(
            parsed.hostname, 443, type=socket.SOCK_STREAM
        )
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                return "Blocked: private or internal network address."

        response = requests.get(
            path,
            timeout=12,
            allow_redirects=False,
            headers={"User-Agent": "ResearchAgent/1.0"},
            stream=True,
        )

        if response.status_code != 200:
            response.close()
            return f"Could not read source: HTTP {response.status_code}"

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > 4_000_000:
            response.close()
            return "Source is too large to read."

        content = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            content.extend(chunk)
            if len(content) > 4_000_000:
                response.close()
                return "Source exceeded the 4 MB limit."

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()
        response.close()

        if (
            "application/pdf" in content_type
            or path.lower().endswith(".pdf")
        ):
            pdf = PdfReader(BytesIO(content))
            text = "\n".join(
                page.extract_text() or ""
                for page in pdf.pages[:8]
            )
        elif "text/html" in content_type:
            soup = BeautifulSoup(
                content.decode("utf-8", errors="replace"),
                "html.parser",
            )
            for tag in soup(
                ["script", "style", "nav", "footer", "header"]
            ):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
        else:
            return "Unsupported source format; use the search snippet."

        return text[:10000] or "No readable text found."

    except Exception as exc:
        return f"Source reading failed: {type(exc).__name__}"
