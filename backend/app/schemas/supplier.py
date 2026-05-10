from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[str] = "enabled"


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class SupplierOut(BaseModel):
    id: int
    name: str
    contact_person: Optional[str]
    contact_phone: Optional[str]
    remark: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
