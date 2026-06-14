"""
User / Auth Schemas
────────────────────
Pydantic models for authentication endpoints.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Request body for POST /auth/register"""

    email: str = Field(
        ...,
        max_length=255,
        description="User email address",
        examples=["user@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 chars, alphanumeric + underscores)",
        examples=["johndoe"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must include uppercase, lowercase, digit)",
        examples=["SecureP@ss123"],
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    """Request body for POST /auth/login"""

    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token TTL in seconds")


class UserResponse(BaseModel):
    """Public user info."""

    id: uuid.UUID
    email: str
    username: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RefreshTokenRequest(BaseModel):
    """Request body for POST /auth/refresh"""

    refresh_token: str


class AuthResponse(BaseModel):
    """Authentication response excluding raw tokens in body."""

    user: UserResponse
    expires_in: int


class RefreshResponse(BaseModel):
    """Refresh token response containing only the token expiration time."""

    expires_in: int
