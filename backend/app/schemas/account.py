from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


AccountType = Literal["bank", "wechat", "alipay", "cash", "pos", "other"]


class AccountCreate(BaseModel):
    name: str
    type: AccountType
    user_id: Optional[int] = None
    remark: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    user_id: Optional[int] = None
    remark: Optional[str] = None
    status: Optional[Literal["enabled", "disabled"]] = None


class AccountOut(BaseModel):
    id: int
    name: str
    type: str
    user_id: Optional[int]
    user_name: Optional[str] = None
    remark: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
