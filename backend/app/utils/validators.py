"""
URL Validators
───────────────
Validation utilities for URL safety and format.

SECURITY NOTE:
- Never trust user-provided URLs blindly
- Validate format, scheme, and check against known malicious URLs
- Prevent SSRF by blocking private/internal IPs
"""

import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Known dangerous URL patterns
BLOCKED_PATTERNS = [
    r"javascript:",
    r"data:",
    r"vbscript:",
    r"file://",
    r"ftp://",
]

# Private IP ranges (prevent SSRF)
PRIVATE_IP_PATTERNS = [
    r"^127\.",
    r"^10\.",
    r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
    r"^192\.168\.",
    r"^0\.",
    r"^localhost",
    r"^::1$",
    r"^\[::1\]",
]


def is_valid_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format and safety.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check scheme
    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    # Check hostname exists
    if not parsed.hostname:
        return False, "URL must have a valid hostname"

    # Check for dangerous schemes
    for pattern in BLOCKED_PATTERNS:
        if re.match(pattern, url, re.IGNORECASE):
            return False, f"URL scheme not allowed"

    # Check for private IPs (SSRF prevention)
    hostname = parsed.hostname
    for pattern in PRIVATE_IP_PATTERNS:
        if re.match(pattern, hostname, re.IGNORECASE):
            return False, "URLs pointing to private/internal addresses are not allowed"

    # Basic length check
    if len(url) > 2048:
        return False, "URL exceeds maximum length (2048 characters)"

    return True, ""


def sanitize_url(url: str) -> str:
    """
    Sanitize URL by stripping dangerous characters.
    Preserves the original URL structure while removing potential XSS vectors.
    """
    # Strip whitespace
    url = url.strip()
    
    # Remove null bytes
    url = url.replace("\x00", "")
    
    # Remove control characters
    url = re.sub(r"[\x01-\x1f\x7f]", "", url)
    
    return url
