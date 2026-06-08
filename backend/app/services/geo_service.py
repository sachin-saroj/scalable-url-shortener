"""
Geo-location Service
─────────────────────
Resolves IP addresses to country/city using MaxMind GeoLite2.

ARCHITECTURE:
- GeoLite2 database loaded once at startup (~60MB RAM)
- O(1) lookups per request
- Graceful fallback if database not available

SETUP:
- Download GeoLite2-City.mmdb from MaxMind (free account required)
- Place in backend/data/GeoLite2-City.mmdb
- If not available, geo features are silently disabled
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to import geoip2
try:
    import geoip2.database

    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False
    logger.warning("geoip2 not available — geo-location features disabled")

# Path to GeoLite2 database
GEOIP_DB_PATH = Path(__file__).parent.parent.parent / "data" / "GeoLite2-City.mmdb"

# Global reader (loaded once)
_reader: Any = None


def _get_reader() -> Any:
    """Lazy-load the GeoIP reader."""
    global _reader
    if _reader is None and GEOIP_AVAILABLE and GEOIP_DB_PATH.exists():
        try:
            _reader = geoip2.database.Reader(str(GEOIP_DB_PATH))
            logger.info("GeoIP database loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load GeoIP database: {e}")
    return _reader


def get_location(ip_address: str) -> dict[str, str | None]:
    """
    Resolve an IP address to geographic location.

    Returns:
        Dict with 'country' and 'city' (or None if unavailable)
    """
    result: dict[str, str | None] = {"country": None, "city": None}

    if not ip_address or ip_address in ("127.0.0.1", "::1", "localhost"):
        return result

    reader = _get_reader()
    if reader is None:
        return result

    try:
        response = reader.city(ip_address)
        result["country"] = response.country.name
        result["city"] = response.city.name
    except Exception:
        # IP not found in database — normal for private/internal IPs
        pass

    return result
