"""
Auth Service
─────────────
JWT authentication with bcrypt password hashing.

SECURITY DECISIONS:
- bcrypt: Adaptive cost factor, resistant to GPU/ASIC attacks
- JWT access tokens: Short-lived (1h), stateless verification
- JWT refresh tokens: Longer-lived (7d), used to get new access tokens
- Password is NEVER stored in plain text or logged

COMMON MISTAKES AVOIDED:
1. Using MD5/SHA for passwords (too fast = brute-forceable)
2. Not setting token expiry (tokens valid forever)
3. Storing tokens in localStorage (XSS vulnerable)
4. Not validating token type (refresh token used as access token)
"""

import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID

from jose import jwt, JWTError
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Password Hashing ──────────────────────────────────
def hash_password(password: str) -> str:
    # Hash a password using bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    # Verify a password against a hash
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


class AuthService:
    """Handles user registration, login, and JWT token management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, request: UserRegisterRequest) -> tuple[UserResponse, TokenResponse]:
        """
        Register a new user.
        
        FLOW:
        1. Check if email/username already exists
        2. Hash password with bcrypt
        3. Create user record
        4. Generate JWT tokens
        5. Return user info + tokens
        """
        # Check email uniqueness
        email_exists = await self._check_email_exists(request.email)
        if email_exists:
            raise ValueError("Email already registered")

        # Check username uniqueness
        username_exists = await self._check_username_exists(request.username)
        if username_exists:
            raise ValueError("Username already taken")

        # Hash password
        password_hash = hash_password(request.password)

        # Create user
        user = User(
            email=request.email,
            username=request.username,
            password_hash=password_hash,
            role="user",
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Generate tokens
        tokens = self._create_tokens(user)

        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            created_at=user.created_at,
        )

        logger.info(f"New user registered: {user.username}")
        return user_response, tokens

    async def login(self, request: UserLoginRequest) -> tuple[UserResponse, TokenResponse]:
        """
        Authenticate user and return JWT tokens.
        
        SECURITY:
        - Same error message for wrong email or wrong password
          (prevents user enumeration attacks)
        """
        # Find user
        user = await self._find_by_email(request.email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is deactivated")

        # Generate tokens
        tokens = self._create_tokens(user)

        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            created_at=user.created_at,
        )

        return user_response, tokens

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Generate new token pair from valid refresh token."""
        payload = self._verify_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        
        user = await self._find_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("Invalid refresh token")

        return self._create_tokens(user)

    async def get_current_user(self, token: str) -> User:
        """Validate access token and return user."""
        payload = self._verify_token(token, expected_type="access")
        user_id = payload.get("sub")
        
        user = await self._find_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or deactivated")

        return user

    # ── Token Management ───────────────────────────────

    def _create_tokens(self, user: User) -> TokenResponse:
        """Generate access + refresh token pair."""
        now = datetime.now(timezone.utc)

        # Access token (short-lived)
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        access_token = jwt.encode(
            access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        # Refresh token (long-lived)
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        refresh_token = jwt.encode(
            refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def _verify_token(self, token: str, expected_type: str) -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")

        # Verify token type
        if payload.get("type") != expected_type:
            raise ValueError(f"Expected {expected_type} token, got {payload.get('type')}")

        return payload

    # ── Private Helpers ────────────────────────────────

    async def _find_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email.lower())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _find_by_id(self, user_id: UUID) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _check_email_exists(self, email: str) -> bool:
        query = select(func.count(User.id)).where(User.email == email.lower())
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0

    async def _check_username_exists(self, username: str) -> bool:
        query = select(func.count(User.id)).where(User.username == username)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0


# Need this import for _check_email_exists and _check_username_exists
from sqlalchemy import func
