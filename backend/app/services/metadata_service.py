"""
Metadata Service
────────────────
Fetches basic OpenGraph and HTML title metadata for a destination URL.
Best-effort operation: failure should never block URL shortening flows.
"""

import httpx
from bs4 import BeautifulSoup


async def fetch_url_metadata(url: str) -> dict[str, str | None]:
    """
    Fetch and parse HTML title, OpenGraph image, and description from a URL.
    Returns a dictionary of findings, with None for missing attributes.
    """
    result: dict[str, str | None] = {"title": None, "og_image": None, "description": None}
    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "LinkForge/1.0"})
            if "text/html" not in resp.headers.get("content-type", "").lower():
                return result

            # Cap the read content size to parse efficiently
            soup = BeautifulSoup(resp.text[:200_000], "html.parser")

            if soup.title and soup.title.string:
                result["title"] = soup.title.string.strip()[:200]

            # Try og:title if normal title is missing or empty
            og_title = soup.find("meta", property="og:title")
            if not result["title"] and og_title and og_title.get("content"):
                result["title"] = str(og_title.get("content")).strip()[:200]

            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                result["og_image"] = str(og_image.get("content"))[:500]

            desc = soup.find("meta", attrs={"name": "description"})
            if desc and desc.get("content"):
                result["description"] = str(desc.get("content"))[:300]

            og_desc = soup.find("meta", property="og:description")
            if not result["description"] and og_desc and og_desc.get("content"):
                result["description"] = str(og_desc.get("content"))[:300]

    except Exception:
        # Best-effort: failures never block creation
        pass

    return result
