from pydantic import BaseModel
from datetime import datetime
from typing import Literal


UserRole = Literal["system_admin", "admin", "assistant"]


class UserCreate(BaseModel):
    name: str
    phone: str
    role: UserRole = "assistant"
    password: str
    remark: str | None = None


class ResetPasswordRequest(BaseModel):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    # 手机号不可编辑
    role: UserRole | None = None
    status: Literal["enabled", "disabled"] | None = None
    remark: str | None = None


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    status: str
    last_login: datetime | None
    created_at: datetime
    remark: str | None

    model_config = {"from_attributes": True}
