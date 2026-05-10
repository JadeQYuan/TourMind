from pydantic import BaseModel
from typing import Any, Generic, TypeVar


T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None


class PageMeta(BaseModel):
    total: int
    page: int
    page_size: int


class PagedResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None
    meta: PageMeta | None = None
