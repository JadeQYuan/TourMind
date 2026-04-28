from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    user_name: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    detail: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AuditLogOut]
