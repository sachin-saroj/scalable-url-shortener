"""
Client IP resolution with trusted-proxy validation.

WHY?
- X-Forwarded-For is attacker-controlled unless a trusted reverse proxy
  overwrites it before the request reaches us.
- We only trust the header if request.client.host (the direct TCP peer)
  is in our configured trusted proxy list.
"""

from fastapi import Request

from app.config import get_settings

settings = get_settings()


def get_client_ip(request: Request) -> str:
    direct_peer = request.client.host if request.client else "unknown"

    trusted = settings.trusted_proxies_list
    if trusted and direct_peer in trusted:
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            # First IP in the chain = original client
            return xff.split(",")[0].strip()

    return direct_peer
