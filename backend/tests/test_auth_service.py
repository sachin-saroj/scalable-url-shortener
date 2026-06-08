"""
Tests for AuthService
──────────────────────
Unit and integration tests for user registration, authentication, and token management.
"""

import pytest
import pytest_asyncio
from jose import jwt
from uuid import uuid4
from app.services.auth_service import AuthService
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.models.user import User
from app.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
class TestAuthService:
    """Test suite for AuthService business logic."""

    async def test_register_success(self, db_session):
        service = AuthService(db_session)
        request = UserRegisterRequest(
            email="test@example.com",
            username="testuser",
            password="SecurePassword123"
        )
        user_resp, token_resp = await service.register(request)

        # Assertions
        assert user_resp.email == "test@example.com"
        assert user_resp.username == "testuser"
        assert user_resp.role == "user"
        assert token_resp.access_token is not None
        assert token_resp.refresh_token is not None

        # Verify password hashing
        user = await service._find_by_email("test@example.com")
        assert user is not None
        assert user.password_hash != "SecurePassword123"

    async def test_register_duplicate_email(self, db_session):
        service = AuthService(db_session)
        request1 = UserRegisterRequest(
            email="duplicate@example.com",
            username="user1",
            password="Password123"
        )
        await service.register(request1)

        request2 = UserRegisterRequest(
            email="DUPLICATE@example.com",  # case insensitivity check
            username="user2",
            password="Password123"
        )
        with pytest.raises(ValueError, match="Email already registered"):
            await service.register(request2)

    async def test_register_duplicate_username(self, db_session):
        service = AuthService(db_session)
        request1 = UserRegisterRequest(
            email="user1@example.com",
            username="duplicate_user",
            password="Password123"
        )
        await service.register(request1)

        request2 = UserRegisterRequest(
            email="user2@example.com",
            username="duplicate_user",
            password="Password123"
        )
        with pytest.raises(ValueError, match="Username already taken"):
            await service.register(request2)

    async def test_login_success(self, db_session):
        service = AuthService(db_session)
        # Setup user
        reg_req = UserRegisterRequest(
            email="login@example.com",
            username="loginuser",
            password="MyPassword123"
        )
        await service.register(reg_req)

        # Attempt login
        login_req = UserLoginRequest(
            email="login@example.com",
            password="MyPassword123"
        )
        user_resp, token_resp = await service.login(login_req)

        assert user_resp.username == "loginuser"
        assert token_resp.access_token is not None

    async def test_login_invalid_email(self, db_session):
        service = AuthService(db_session)
        login_req = UserLoginRequest(
            email="nonexistent@example.com",
            password="Password123"
        )
        with pytest.raises(ValueError, match="Invalid email or password"):
            await service.login(login_req)

    async def test_login_invalid_password(self, db_session):
        service = AuthService(db_session)
        reg_req = UserRegisterRequest(
            email="login_fail@example.com",
            username="loginfail",
            password="CorrectPassword123"
        )
        await service.register(reg_req)

        login_req = UserLoginRequest(
            email="login_fail@example.com",
            password="WrongPassword123"
        )
        with pytest.raises(ValueError, match="Invalid email or password"):
            await service.login(login_req)

    async def test_login_deactivated_account(self, db_session):
        service = AuthService(db_session)
        reg_req = UserRegisterRequest(
            email="deactivated@example.com",
            username="deactivateduser",
            password="Password123"
        )
        await service.register(reg_req)

        # Deactivate user
        user = await service._find_by_email("deactivated@example.com")
        user.is_active = False
        await db_session.commit()

        login_req = UserLoginRequest(
            email="deactivated@example.com",
            password="Password123"
        )
        with pytest.raises(ValueError, match="Account is deactivated"):
            await service.login(login_req)

    async def test_refresh_tokens_success(self, db_session):
        service = AuthService(db_session)
        reg_req = UserRegisterRequest(
            email="refresh@example.com",
            username="refreshuser",
            password="Password123"
        )
        _, token_resp = await service.register(reg_req)

        # Use refresh token to get new tokens
        new_tokens = await service.refresh_tokens(token_resp.refresh_token)
        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None

    async def test_refresh_tokens_invalid_type(self, db_session):
        service = AuthService(db_session)
        reg_req = UserRegisterRequest(
            email="refresh_invalid@example.com",
            username="refreshinvalid",
            password="Password123"
        )
        _, token_resp = await service.register(reg_req)

        # Passing access_token instead of refresh_token
        with pytest.raises(ValueError, match="Expected refresh token"):
            await service.refresh_tokens(token_resp.access_token)

    async def test_refresh_tokens_deactivated_user(self, db_session):
        service = AuthService(db_session)
        reg_req = UserRegisterRequest(
            email="refresh_deact@example.com",
            username="refreshdeact",
            password="Password123"
        )
        _, token_resp = await service.register(reg_req)

        # Deactivate user
        user = await service._find_by_email("refresh_deact@example.com")
        user.is_active = False
        await db_session.commit()

        with pytest.raises(ValueError, match="Invalid refresh token"):
            await service.refresh_tokens(token_resp.refresh_token)

    async def test_get_current_user_success(self, db_session):
        service = AuthService(db_session)
        reg_req = UserRegisterRequest(
            email="currentuser@example.com",
            username="currentuser",
            password="Password123"
        )
        _, token_resp = await service.register(reg_req)

        user = await service.get_current_user(token_resp.access_token)
        assert user.username == "currentuser"
        assert user.email == "currentuser@example.com"

    async def test_get_current_user_not_found(self, db_session):
        service = AuthService(db_session)
        # Generate token with random sub UUID
        random_sub = str(uuid4())
        token = jwt.encode(
            {"sub": random_sub, "type": "access"},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        with pytest.raises(ValueError, match="User not found or deactivated"):
            await service.get_current_user(token)

    async def test_verify_token_corrupted(self, db_session):
        service = AuthService(db_session)
        with pytest.raises(ValueError, match="Invalid token"):
            service._verify_token("invalid.jwt.token", expected_type="access")
