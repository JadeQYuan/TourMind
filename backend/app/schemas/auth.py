from pydantic import BaseModel
from datetime import datetime


class LoginRequest(BaseModel):
    username: str   # 手机号
    password: str
    remember_me: bool = False


class LoginUserInfo(BaseModel):
    id: int
    full_name: str
    role: str
    must_change_password: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserInfo


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    phone: str | None
    employee_id: str | None
    role: str
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
