from fastapi import Response

from app.config import Settings
from app.schemas.user import TokenResponse


def set_auth_cookies(response: Response, tokens: TokenResponse, settings: Settings) -> None:
    """Set access_token and refresh_token httponly cookies with consistent options."""
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # FIX: matches JWT exp
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    """Clear access_token and refresh_token cookies."""
    for key in ("access_token", "refresh_token"):
        response.delete_cookie(
            key=key,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
        )
