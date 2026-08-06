from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginCredentials(BaseModel):
    username: str = Field(..., description="Email or Mobile Number")
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class SendOTPRequest(BaseModel):
    mobile_number: str = Field(..., max_length=15)

class VerifyOTPRequest(BaseModel):
    mobile_number: str = Field(..., max_length=15)
    otp_code: str = Field(..., min_length=4, max_length=6)

class ResetPasswordRequest(BaseModel):
    mobile_number: str = Field(..., max_length=15)
    otp_code: str = Field(..., min_length=4, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)

class OTPResponse(BaseModel):
    message: str
    mobile_number: str
    dev_otp: str | None = None
