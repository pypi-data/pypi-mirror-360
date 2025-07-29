from typing import Any, TypeVar, Generic

from pydantic import BaseModel
from pydantic.generics import GenericModel


__all__ = (
    "SuccessResponse",
    "FailedResponse",
)


T = TypeVar('T')


class ResponseBase(BaseModel):
    success: bool


class SuccessResponse(GenericModel, Generic[T]):
    success: bool = True
    data: Any


class FailedResponse(ResponseBase):
    success: bool = False
    message: str
