
from pydantic import BaseModel, ConfigDict


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


