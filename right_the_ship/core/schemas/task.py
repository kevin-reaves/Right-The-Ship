from pydantic import Field, conint, model_validator
from typing import List, Optional
from datetime import date

from right_the_ship.core.schemas.custom_base_model import CustomBaseModel
from right_the_ship.core.validators.task_validators import (
    validate_end_date,
    validate_day_of_week,
    validate_day_of_month,
    validate_task_types,
)


class SingleTaskIn(CustomBaseModel):
    end_date: date

    @model_validator(mode="before")
    def validate_end_date(cls, values):
        return validate_end_date(cls, values)


class SingleTaskUpdateIn(CustomBaseModel):
    end_date: Optional[date]

    @model_validator(mode="before")
    def validate_end_date(cls, values):
        return validate_end_date(cls, values)


class WeeklyRecurrenceIn(CustomBaseModel):
    day_of_week: conint(ge=0, le=6)  # 0 = Monday, 6 = Sunday

    @model_validator(mode="before")
    def validate_day_of_week(cls, values):
        return validate_day_of_week(cls, values)


class BiweeklyRecurrenceIn(CustomBaseModel):
    day_of_week: conint(ge=0, le=6)

    @model_validator(mode="before")
    def validate_day_of_week(cls, values):
        return validate_day_of_week(cls, values)


class MonthlyRecurrenceIn(CustomBaseModel):
    day_of_month: conint(ge=1, le=31)

    @model_validator(mode="before")
    def validate_day_of_month(cls, values):
        return validate_day_of_month(cls, values)


class RecurringTaskIn(CustomBaseModel):
    frequency: str = Field(
        ..., pattern="^(DAILY|WEEKLY|TWICE_WEEKLY|BIWEEKLY|MONTHLY)$"
    )
    end_date: date
    days_of_week: Optional[List[WeeklyRecurrenceIn]] = None
    days_of_month: Optional[List[MonthlyRecurrenceIn]] = None

    @model_validator(mode="before")
    def validate_end_date(cls, values):
        return validate_end_date(cls, values)

    @model_validator(mode="before")
    def validate_days(cls, values):
        frequency = values.get("frequency")
        if frequency == "WEEKLY" and not values.get("days_of_week"):
            raise ValueError("days_of_week is required for WEEKLY tasks")
        if frequency in {"TWICE_WEEKLY", "BIWEEKLY"} and not values.get("days_of_week"):
            raise ValueError(
                "days_of_week is required for TWICE_WEEKLY and BIWEEKLY tasks"
            )
        if frequency == "MONTHLY" and not values.get("days_of_month"):
            raise ValueError("days_of_month is required for MONTHLY tasks")
        return values


class RecurringTaskUpdateIn(CustomBaseModel):
    end_date: Optional[date]
    frequency: Optional[str] = Field(
        None, pattern="^(DAILY|WEEKLY|TWICE_WEEKLY|BIWEEKLY|MONTHLY)$"
    )
    days_of_week: Optional[List[WeeklyRecurrenceIn]] = None
    days_of_month: Optional[List[MonthlyRecurrenceIn]] = None


class TaskIn(CustomBaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    task_type: str = Field(..., pattern="^(SINGLE|RECURRING)$")
    start_date: date
    single_task: Optional[SingleTaskIn] = None
    recurring_task: Optional[RecurringTaskIn] = None

    @model_validator(mode="before")
    def validate_task_types(cls, values):
        return validate_task_types(cls, values)


class TaskUpdateIn(CustomBaseModel):
    # user_id is not updatable
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date]
    single_task: Optional[SingleTaskUpdateIn] = None
    recurring_task: Optional[RecurringTaskUpdateIn] = None

    @model_validator(mode="before")
    def validate_task_types(cls, values):
        return validate_task_types(cls, values)
