import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_list_vehicles(client: AsyncClient):
    # 1. Login as Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "test_token"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Extract user ID from token to use as owner_id
    import jwt
    payload = jwt.decode(token, options={"verify_signature": False})
    user_id = int(payload["sub"])

    # 3. Create Vehicle
    vehicle_payload = {
        "owner_id": user_id,
        "vehicle_type": "SEDAN",
        "registration_number": "MH01AB1234",
        "brand": "Toyota",
        "model": "Etios",
        "color": "White",
        "year_of_manufacture": 2021,
        "seating_capacity": 4
    }

    res = await client.post(
        "/api/v1/fleet/vehicles",
        json=vehicle_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["registration_number"] == "MH01AB1234"
    vehicle_id = data["id"]

    # 3. List Vehicles
    list_res = await client.get(
        "/api/v1/fleet/vehicles",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_res.status_code == 200
    vehicles = list_res.json()
    assert len(vehicles) >= 1
    assert any(v["id"] == vehicle_id for v in vehicles)
