import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.fixture
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


async def test_register(client: AsyncClient):
    resp = await client.post(
        "/register/",
        json={"email": "new@example.com", "password": "pass123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


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


async def test_token_invalid(client: AsyncClient):
    resp = await client.post(
        "/token/",
        data={"username": "nonexistent@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_create_order(client: AsyncClient, auth_headers):
    resp = await client.post(
        "/orders/",
        json={"items": [{"name": "item1", "quantity": 2, "price": 10.0}]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PENDING"
    assert data["total_price"] == 20.0
    assert "id" in data


async def test_create_order_unauthorized(client: AsyncClient):
    resp = await client.post(
        "/orders/",
        json={"items": []},
    )
    assert resp.status_code == 401


async def test_get_order(client: AsyncClient, test_user, auth_headers):
    create_resp = await client.post(
        "/orders/",
        json={"items": [{"name": "x", "quantity": 1, "price": 5.0}]},
        headers=auth_headers,
    )
    order_id = create_resp.json()["id"]
    resp = await client.get(f"/orders/{order_id}/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


async def test_get_order_forbidden(client: AsyncClient, auth_headers, registered_user):
    create_resp = await client.post(
        "/orders/",
        json={"items": []},
        headers=auth_headers,
    )
    order_id = create_resp.json()["id"]
    resp = await client.get(f"/orders/{order_id}/", headers=registered_user)
    assert resp.status_code == 403


async def test_patch_order(client: AsyncClient, auth_headers):
    create_resp = await client.post(
        "/orders/",
        json={"items": [{"name": "item", "quantity": 1, "price": 1.0}]},
        headers=auth_headers,
    )
    order_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/orders/{order_id}/",
        json={"status": "PAID"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "PAID"


async def test_get_orders_by_user(client: AsyncClient, test_user, auth_headers):
    resp = await client.get(
        f"/orders/user/{test_user.id}/",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_orders_by_user_forbidden(client: AsyncClient, auth_headers):
    resp = await client.get("/orders/user/99999/", headers=auth_headers)
    assert resp.status_code == 403
