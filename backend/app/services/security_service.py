"""
Security Service
─────────────────
URL safety validation and malicious link detection.

LAYERS OF DEFENSE:
1. URL format validation (handled by validators.py)
2. SSRF prevention (private IP blocking)
3. Google Safe Browsing API (if API key provided)
4. Pattern-based suspicious URL detection

WHY multi-layer?
- No single method catches everything
- Defense in depth is a security best practice
- Graceful degradation if external API is unavailable
"""

import logging
import re

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Known phishing/spam patterns
SUSPICIOUS_PATTERNS = [
    r"bit\.ly/.*bit\.ly",  # Nested shorteners
    r"login.*password",  # Credential phishing
    r"verify.*account.*suspended",  # Account scam patterns
    r"\.exe$",  # Direct executable links
    r"\.scr$",  # Screensaver (malware vector)
    r"\.bat$",  # Batch files
]


async def check_url_safety(url: str) -> tuple[bool, str]:
    """
    Check if a URL is safe to shorten.

    Returns:
        Tuple of (is_safe, reason)
    """
    # Layer 1: Pattern-based check (fast, no external call)
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return False, "URL matches a known suspicious pattern"

    # Layer 2: Google Safe Browsing API (if configured)
    if settings.GOOGLE_SAFE_BROWSING_API_KEY:
        is_safe, reason = await _check_google_safe_browsing(url)
        if not is_safe:
            return False, reason

    return True, "URL appears safe"


async def _check_google_safe_browsing(url: str) -> tuple[bool, str]:
    """
    Check URL against Google Safe Browsing API.

    TRADE-OFF:
    - Adds ~100ms latency to URL creation (acceptable)
    - Requires Google API key (free but needs setup)
    - Only checks during creation, not on every redirect
    """
    try:
        api_url = (
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find"
            f"?key={settings.GOOGLE_SAFE_BROWSING_API_KEY}"
        )

        payload = {
            "client": {"clientId": "url-shortener", "clientVersion": "1.0.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(api_url, json=payload)
            data = response.json()

        if data.get("matches"):
            threat_type = data["matches"][0].get("threatType", "UNKNOWN")
            return False, f"URL flagged as {threat_type} by Google Safe Browsing"

        return True, "URL is safe"

    except Exception as e:
        # Fail-open: if Google API is down, allow the URL
        logger.warning(f"Google Safe Browsing check failed (allowing): {e}")
        return True, "Safety check unavailable — URL allowed"
