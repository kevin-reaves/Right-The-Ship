from datetime import date
from typing import Optional

from ninja import Schema
from pydantic import Field


class TaskInSchema(Schema):
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, min_length=3, max_length=200)
    due_date: Optional[date] = Field(None, description="Format: yyyy-mm-dd")
    completed: bool = Field(False)
    frequency: Optional[str] = Field(None, min_length=3, max_length=10)
    start_date: Optional[date] = Field(None, description="Format: yyyy-mm-dd")
    end_date: Optional[date] = Field(None, description="Format: yyyy-mm-dd")
    user_id: int = Field(..., gt=0)
    day: Optional[int] = Field(None, gte=0, lt=32)


class TaskSchema(Schema):
    id: Optional[int]
    title: str
    description: Optional[str]
    due_date: Optional[date]
    completed: bool


class TaskDetailSchema(Schema):
    task: TaskSchema
    is_recurring: bool
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    day: Optional[int] = None
