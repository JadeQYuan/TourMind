from pydantic import BaseModel
from datetime import datetime


class LoginRequest(BaseModel):
    username: str   # 手机号
    password: str
    remember_me: bool = False


class LoginUserInfo(BaseModel):
    id: int
    name: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserInfo


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserOut(BaseModel):
    id: int
    name: str
    phone: str | None
    role: str
    status: str
    last_login: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
