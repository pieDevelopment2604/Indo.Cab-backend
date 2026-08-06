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
