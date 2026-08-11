import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_pricing_zone(client: AsyncClient):
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "test_token"}
    )
    token = login_res.json()["token"]

    zone_payload = {
        "name": "Mumbai Metropolitan",
        "zone_type": "CITY",
        "cities": ["Mumbai", "Thane", "Navi Mumbai"]
    }

    res = await client.post(
        "/api/v1/pricing/zones",
        json=zone_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    assert res.json()["name"] == "Mumbai Metropolitan"
