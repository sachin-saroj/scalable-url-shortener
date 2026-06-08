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
import ipaddress
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Known dangerous URL patterns (XSS/phishing/unsupported protocols)
BLOCKED_PATTERNS = [
    r"javascript:",
    r"data:",
    r"vbscript:",
    r"file://",
    r"ftp://",
]

# Private IP patterns for string-based SSRF blocking
PRIVATE_IP_PATTERNS = [
    r"^127\.",                           # Loopback (127.x.x.x)
    r"^10\.",                            # Private class A (10.x.x.x)
    r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",   # Private class B (172.16.x.x - 172.31.x.x)
    r"^192\.168\.",                      # Private class C (192.168.x.x)
    r"^0\.",                             # Unspecified / system (0.x.x.x)
    r"^169\.254\.",                      # Link-local (169.254.x.x)
    r"^localhost",                       # Localhost hostname
    r"^::1$",                            # IPv6 Loopback
    r"^\[::1\]",                         # IPv6 Loopback bracketed
]


def is_valid_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format and safety (including SSRF protection).
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Basic length check
    if len(url) > 2048:
        return False, "URL exceeds maximum length (2048 characters)"

    # Scheme check: must be strictly http or https
    if not url.startswith(("http://", "https://")):
        return False, "URL scheme must be http or https"

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    # Check hostname exists
    hostname = parsed.hostname
    if not hostname:
        return False, "URL must have a valid hostname"

    hostname_lower = hostname.lower().strip()

    # Check for dangerous schemes
    for pattern in BLOCKED_PATTERNS:
        if re.match(pattern, url, re.IGNORECASE):
            return False, "URL scheme not allowed"

    # 1. String-based blocking of private/internal addresses
    for pattern in PRIVATE_IP_PATTERNS:
        if re.match(pattern, hostname_lower, re.IGNORECASE):
            return False, "URLs pointing to private/internal addresses are not allowed"

    # 2. IP address check (if hostname is a raw IP)
    try:
        ip = ipaddress.ip_address(hostname_lower)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_reserved:
            return False, "URLs pointing to private/internal addresses are not allowed"
    except ValueError:
        # Hostname is not an IP address, which is normal for domains
        pass

    # 3. DNS resolution safety check to prevent DNS rebinding SSRF
    try:
        addr_info = socket.getaddrinfo(hostname_lower, None)
        for info in addr_info:
            ip_str = info[4][0]
            try:
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_reserved:
                    return False, "URLs pointing to private/internal addresses are not allowed"
            except ValueError:
                pass
    except socket.gaierror:
        # Offline/Unresolved domain handling
        # Allow unresolved domains (useful for testing and offline dev),
        # but block known local top-level domains.
        if hostname_lower.endswith((".local", ".localhost", ".internal")):
            return False, "URLs pointing to local domains are not allowed"

    return True, ""


def validate_url_safety(url: str) -> None:
    """
    Reusable validator for URL safety.
    Raises ValueError if URL is invalid or unsafe (SSRF attempt).
    """
    is_valid, error_msg = is_valid_url(url)
    if not is_valid:
        raise ValueError(error_msg)


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
