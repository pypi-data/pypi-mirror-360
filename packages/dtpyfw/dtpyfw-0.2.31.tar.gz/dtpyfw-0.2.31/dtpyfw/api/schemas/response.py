from typing import Any, TypeVar, Generic

from pydantic import BaseModel


__all__ = (
    "ResponseBase",
    "SuccessResponse",
    "FailedResponse",
)


T = TypeVar('T')


class ResponseBase(BaseModel):
    success: bool


class SuccessResponse(ResponseBase, Generic[T]):
    success: bool = True
    data: Any


class FailedResponse(ResponseBase):
    success: bool = False
    message: str
