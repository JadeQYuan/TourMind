from pydantic import BaseModel
from datetime import datetime
from typing import Literal


UserRole = Literal["system_admin", "admin", "assistant"]


class UserCreate(BaseModel):
    username: str | None = None
    full_name: str
    phone: str | None = None
    employee_id: str | None = None
    role: UserRole = "assistant"


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    employee_id: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: int
    username: str | None
    full_name: str
    phone: str | None
    employee_id: str | None
    role: str
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreateResponse(UserOut):
    """Returned only on POST /users and POST /users/{id}/reset-password — contains the one-time password."""
    generated_password: str


class ResetPasswordResponse(BaseModel):
    generated_password: str
