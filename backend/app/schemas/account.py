from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


AccountType = Literal["bank", "wechat", "alipay", "cash", "pos", "other"]


class AccountCreate(BaseModel):
    name: str
    account_type: AccountType
    description: Optional[str] = None
    user_id: Optional[int] = None
    notes: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[AccountType] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class AccountOut(BaseModel):
    id: int
    name: str
    account_type: str
    description: Optional[str]
    user_id: Optional[int]
    user_name: Optional[str] = None
    notes: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
