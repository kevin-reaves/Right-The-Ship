from typing import Optional

from ninja import Schema
from pydantic import Field


class UserIn(Schema):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)


class UserUpdateIn(Schema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=3, max_length=50)


class UserOut(Schema):
    id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
