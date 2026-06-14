"""
Auth Endpoints
───────────────
POST /api/v1/auth/register  — Register new user
POST /api/v1/auth/login     — Login and get tokens
POST /api/v1/auth/refresh   — Refresh access token
GET  /api/v1/auth/me        — Get current user info
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status

from app.dependencies import DB, CurrentUser, check_auth_rate_limit
from app.schemas.user import (
    AuthResponse,
    RefreshResponse,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.auth_cookies import clear_auth_cookies, set_auth_cookies

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    dependencies=[Depends(check_auth_rate_limit)],
)
async def register(request: UserRegisterRequest, db: DB, response: Response):
    """Register a new user account."""
    auth_service = AuthService(db)
    try:
        user, tokens = await auth_service.register(request)
        from app.config import get_settings

        settings = get_settings()
        set_auth_cookies(response, tokens, settings)
        return AuthResponse(
            user=UserResponse.model_validate(user),
            expires_in=tokens.expires_in,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login",
    dependencies=[Depends(check_auth_rate_limit)],
)
async def login(request: UserLoginRequest, db: DB, response: Response):
    """Login with email and password."""
    auth_service = AuthService(db)
    try:
        user, tokens = await auth_service.login(request)
        from app.config import get_settings

        settings = get_settings()
        set_auth_cookies(response, tokens, settings)
        return AuthResponse(
            user=UserResponse.model_validate(user),
            expires_in=tokens.expires_in,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: Request,
    response: Response,
    db: DB,
    body: RefreshTokenRequest | None = Body(default=None),
):
    """Get a new access token using a valid refresh token."""
    refresh_token_val = None
    if body and body.refresh_token:
        refresh_token_val = body.refresh_token
    else:
        refresh_token_val = request.cookies.get("refresh_token")

    if not refresh_token_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    auth_service = AuthService(db)
    try:
        tokens = await auth_service.refresh_tokens(refresh_token_val)
        from app.config import get_settings

        settings = get_settings()
        set_auth_cookies(response, tokens, settings)
        return RefreshResponse(expires_in=tokens.expires_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout",
    summary="Logout",
)
async def logout(response: Response):
    """Logout by clearing HTTP-only cookies."""
    from app.config import get_settings

    settings = get_settings()
    clear_auth_cookies(response, settings)
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_me(user: CurrentUser):
    """Get the currently authenticated user's info."""
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
    )
