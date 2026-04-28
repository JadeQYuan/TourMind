from pydantic import BaseModel, field_validator
from datetime import datetime
import re


class LoginRequest(BaseModel):
    username: str   # 手机号 / 工号 / 用户名
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

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("密码长度不能少于 12 位")
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?/\\`~]', v):
            raise ValueError("密码必须包含特殊字符")
        return v


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
