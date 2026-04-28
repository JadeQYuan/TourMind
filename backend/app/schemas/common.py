from pydantic import BaseModel
from typing import Any


class ResponseModel(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class PageMeta(BaseModel):
    total: int
    page: int
    page_size: int


class PagedResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
    meta: PageMeta | None = None
