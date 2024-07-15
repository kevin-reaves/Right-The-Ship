from typing import Optional
from pydantic import Field

from right_the_ship.core.schemas.custom_base_model import CustomBaseModel


class UserIn(CustomBaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)


class UserUpdateIn(CustomBaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=3, max_length=50)


class UserOut(CustomBaseModel):
    id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
