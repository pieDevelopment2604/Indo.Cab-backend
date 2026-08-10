import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123", "recaptcha_token": "mock_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "wrongpassword", "recaptcha_token": "mock_token"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_missing_recaptcha_fails(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin1@indocab.com", "password": "password123"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_send_and_verify_otp(client: AsyncClient):
    # 1. Send OTP with standard +91 number
    send_res = await client.post("/api/v1/auth/send-otp", json={"mobile_number": "+919999988881", "recaptcha_token": "mock_token"})
    assert send_res.status_code == 200
    otp_data = send_res.json()
    assert "dev_otp" in otp_data
    dev_otp = otp_data["dev_otp"]

    # 2. Verify OTP
    verify_res = await client.post(
        "/api/v1/auth/verify-otp",
        json={"mobile_number": "+919999988881", "otp_code": dev_otp}
    )
    assert verify_res.status_code == 200
    token_data = verify_res.json()
    assert "access_token" in token_data

@pytest.mark.asyncio
async def test_phone_normalization_otp_flow(client: AsyncClient):
    # 1. Send OTP using 12-digit number without plus: "919999988881"
    send_res = await client.post("/api/v1/auth/send-otp", json={"mobile_number": "919999988881", "recaptcha_token": "mock_token"})
    assert send_res.status_code == 200
    dev_otp = send_res.json()["dev_otp"]

    # 2. Verify OTP using 10-digit number without country code: "9999988881"
    verify_res = await client.post(
        "/api/v1/auth/verify-otp",
        json={"mobile_number": "9999988881", "otp_code": dev_otp}
    )
    assert verify_res.status_code == 200
    assert "access_token" in verify_res.json()

@pytest.mark.asyncio
async def test_forgot_and_reset_password(client: AsyncClient):
    # 1. Forgot password
    forgot_res = await client.post("/api/v1/auth/forgot-password", json={"mobile_number": "+919999988882", "recaptcha_token": "mock_token"})
    assert forgot_res.status_code == 200
    dev_otp = forgot_res.json()["dev_otp"]

    # 2. Reset password
    reset_res = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "mobile_number": "+919999988882",
            "otp_code": dev_otp,
            "new_password": "newsecretpassword123"
        }
    )
    assert reset_res.status_code == 200

    # 3. Login with new password
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "+919999988882", "password": "newsecretpassword123", "recaptcha_token": "mock_token"}
    )
    assert login_res.status_code == 200
