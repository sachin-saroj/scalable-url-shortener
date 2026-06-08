"""
Auth Endpoints
───────────────
POST /api/v1/auth/register  — Register new user
POST /api/v1/auth/login     — Login and get tokens
POST /api/v1/auth/refresh   — Refresh access token
GET  /api/v1/auth/me        — Get current user info
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import DB, CurrentUser, check_auth_rate_limit
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    dependencies=[Depends(check_auth_rate_limit)],
)
async def register(request: UserRegisterRequest, db: DB):
    """Register a new user account."""
    auth_service = AuthService(db)
    try:
        user, tokens = await auth_service.register(request)
        return {
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=dict,
    summary="Login",
    dependencies=[Depends(check_auth_rate_limit)],
)
async def login(request: UserLoginRequest, db: DB):
    """Login with email and password."""
    auth_service = AuthService(db)
    try:
        user, tokens = await auth_service.login(request)
        return {
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(request: RefreshTokenRequest, db: DB):
    """Get a new access token using a valid refresh token."""
    auth_service = AuthService(db)
    try:
        tokens = await auth_service.refresh_tokens(request.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


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
