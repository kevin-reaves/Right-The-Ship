from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
