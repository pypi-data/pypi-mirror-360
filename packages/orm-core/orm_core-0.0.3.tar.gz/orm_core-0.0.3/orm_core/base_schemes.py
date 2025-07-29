from pydantic import BaseModel

from typing import Generic, TypeVar

T = TypeVar('T')


class ListDTO(BaseModel, Generic[T]):
    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    content: list[T]

    class Config:
        from_attributes = True


class ResponseStatus(BaseModel):
    status: str = "success"
