from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.db.models import User
from app.services.auth_service import authenticate_user, register_user


@pytest.mark.asyncio
async def test_register_user():
    repo = AsyncMock()
    repo.create = AsyncMock(
        return_value=User(
            id=1,
            email="a@b.com",
            password="hash",
            created_at=datetime.now(timezone.utc),
        )
    )
    user = await register_user(repo, "a@b.com", "password")
    assert user.email == "a@b.com"
    assert user.password == "hash"
    repo.create.assert_called_once_with(email="a@b.com", password=repo.create.call_args[1]["password"])


@pytest.mark.asyncio
async def test_authenticate_user_ok():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock(
        return_value=User(
            id=1,
            email="a@b.com",
            password="$2b$12$dummy",
            created_at=datetime.now(timezone.utc),
        )
    )
    from app.core.security import get_password_hash

    hashed = get_password_hash("right")
    repo.get_by_email.return_value = User(
        id=1, email="a@b.com", password=hashed, created_at=datetime.now(timezone.utc)
    )
    user = await authenticate_user(repo, "a@b.com", "right")
    assert user is not None
    assert user.email == "a@b.com"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    from app.core.security import get_password_hash

    repo = AsyncMock()
    hashed = get_password_hash("right")
    repo.get_by_email = AsyncMock(
        return_value=User(
            id=1, email="a@b.com", password=hashed, created_at=datetime.now(timezone.utc)
        )
    )
    user = await authenticate_user(repo, "a@b.com", "wrong")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    repo = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=None)
    user = await authenticate_user(repo, "a@b.com", "any")
    assert user is None
