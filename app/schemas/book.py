from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    price: float = Field(ge=0)


class BookUpdate(BaseModel):
    """All fields optional - PATCH only touches what the client sends."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=120)
    price: Optional[float] = Field(default=None, ge=0)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    price: float
    created_at: datetime

    model_config = {"from_attributes": True}
