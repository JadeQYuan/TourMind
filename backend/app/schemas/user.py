from pydantic import BaseModel
from datetime import datetime
from typing import Literal


UserRole = Literal["system_admin", "admin", "assistant"]


class UserCreate(BaseModel):
    name: str
    phone: str
    role: UserRole = "assistant"
    password: str


class ResetPasswordRequest(BaseModel):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    # 手机号不可编辑
    role: UserRole | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
