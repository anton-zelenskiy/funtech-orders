import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient):
    await client.post(
        "/register/",
        json={"email": "user@example.com", "password": "secret123"},
    )
    resp = await client.post(
        "/token/",
        data={"username": "user@example.com", "password": "secret123"},
    )
    data = resp.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest_asyncio.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post(
        "/register/",
        json={"email": "new@example.com", "password": "pass123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


@pytest_asyncio.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/register/",
        json={"email": "dup@example.com", "password": "pass123"},
    )
    resp = await client.post(
        "/register/",
        json={"email": "dup@example.com", "password": "other"},
    )
    assert resp.status_code == 400


@pytest_asyncio.mark.asyncio
async def test_token(client: AsyncClient):
    await client.post(
        "/register/",
        json={"email": "token@example.com", "password": "mypass"},
    )
    resp = await client.post(
        "/token/",
        data={"username": "token@example.com", "password": "mypass"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


@pytest_asyncio.mark.asyncio
async def test_token_invalid(client: AsyncClient):
    resp = await client.post(
        "/token/",
        data={"username": "nonexistent@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
