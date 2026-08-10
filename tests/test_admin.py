import random
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_create_vendor(client: AsyncClient):
    # 1. Login as Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "mock_token"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Create Vendor
    rand_num = random.randint(10000, 99999)
    vendor_payload = {
        "email": f"newvendor{rand_num}@indocab.com",
        "mobile_number": f"99999{rand_num}",
        "first_name": "New",
        "last_name": "Vendor",
        "password": "vendorpassword123",
        "company_name": "New Fleet Enterprise",
        "gst_number": "07NEWGST1234Z1",
        "pan_number": "NEWPAN1234",
        "address": "123 Fleet House, Delhi",
        "operating_cities": ["Delhi", "Noida"]
    }

    res = await client.post(
        "/api/v1/admin/vendors",
        json=vendor_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["role"] == "VENDOR"
    assert data["company_name"] == "New Fleet Enterprise"
    assert data["mobile_number"] == f"+9199999{rand_num}"

@pytest.mark.asyncio
async def test_admin_list_and_get_vendors(client: AsyncClient):
    # 1. Login as Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "mock_token"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. List Vendors
    list_res = await client.get(
        "/api/v1/admin/vendors",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_res.status_code == 200
    vendors = list_res.json()
    assert len(vendors) >= 1
    assert vendors[0]["role"] == "VENDOR"

    # 3. Get single Vendor details
    first_vendor_id = vendors[0]["user_id"]
    get_res = await client.get(
        f"/api/v1/admin/vendors/{first_vendor_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_res.status_code == 200
    vendor_data = get_res.json()
    assert vendor_data["user_id"] == first_vendor_id
    assert vendor_data["role"] == "VENDOR"

@pytest.mark.asyncio
async def test_admin_create_and_list_drivers(client: AsyncClient):
    # 1. Login as Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "mock_token"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Get Vendor 1 ID
    vendors_res = await client.get(
        "/api/v1/admin/vendors",
        headers={"Authorization": f"Bearer {token}"}
    )
    vendor_id = vendors_res.json()[0]["user_id"]

    # 3. Create Driver
    rand_num = random.randint(10000, 99999)
    driver_payload = {
        "email": f"newdriver{rand_num}@indocab.com",
        "mobile_number": f"98765{rand_num}",
        "first_name": "Test",
        "last_name": "Driver",
        "password": "driverpassword123",
        "license_number": f"DL-142026{rand_num}",
        "vendor_id": vendor_id
    }

    create_res = await client.post(
        "/api/v1/admin/drivers",
        json=driver_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_res.status_code == 201
    driver_data = create_res.json()
    assert driver_data["role"] == "DRIVER"
    driver_id = driver_data["user_id"]

    # 4. List Drivers
    list_res = await client.get(
        f"/api/v1/admin/drivers?vendor_id={vendor_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_res.status_code == 200
    drivers_list = list_res.json()
    assert len(drivers_list) >= 1

    # 5. Get single Driver
    get_res = await client.get(
        f"/api/v1/admin/drivers/{driver_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["user_id"] == driver_id

@pytest.mark.asyncio
async def test_admin_update_user_status(client: AsyncClient):
    # 1. Login as Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "mock_token"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Get first vendor user_id dynamically
    vendors_res = await client.get(
        "/api/v1/admin/vendors",
        headers={"Authorization": f"Bearer {token}"}
    )
    target_user_id = vendors_res.json()[0]["user_id"]

    # 3. Suspend Vendor
    status_res = await client.patch(
        f"/api/v1/admin/users/{target_user_id}/status",
        json={"status": "SUSPENDED"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "SUSPENDED"

    # 4. Reactivate Vendor
    reactivate_res = await client.patch(
        f"/api/v1/admin/users/{target_user_id}/status",
        json={"status": "ACTIVE"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert reactivate_res.status_code == 200
    assert reactivate_res.json()["status"] == "ACTIVE"

@pytest.mark.asyncio
async def test_admin_add_and_list_clients(client: AsyncClient):
    # 1. Login as Admin
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "mock_token"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 2. Add Corporate Client
    rand_num = random.randint(10000, 99999)
    client_payload = {
        "company_name": f"Corporate Client {rand_num}",
        "contact_person": "Vikram Sethi",
        "email": f"client{rand_num}@corp.com",
        "mobile_number": f"98888{rand_num}",
        "gst_number": "07CORPGST999Z9",
        "pan_number": "CORPPAN999",
        "address": "45 Corporate Tower, Gurgaon",
        "operating_cities": ["Delhi", "Gurgaon"],
        "discount_percentage": 5.0
    }

    add_res = await client.post(
        "/api/v1/admin/clients",
        json=client_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert add_res.status_code == 201
    c_data = add_res.json()
    assert c_data["company_name"] == f"Corporate Client {rand_num}"
    assert c_data["status"] == "ACTIVE"

    # 3. List Corporate Clients
    list_res = await client.get(
        "/api/v1/admin/clients",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_res.status_code == 200
    clients_list = list_res.json()
    assert len(clients_list) >= 1
