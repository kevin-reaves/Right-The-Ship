from datetime import date, datetime


def validate_end_date(cls, values):
    end_date = values.get("end_date")

    if end_date is None:
        raise ValueError("end_date is required for single tasks")

    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end_date < date.today():
        raise ValueError("end_date must be in the future")

    values["end_date"] = end_date
    return values


def validate_day_of_week(cls, values):
    if "day_of_week" not in values or values["day_of_week"] is None:
        raise ValueError("day_of_week is required for weekly and biweekly tasks")

    if values["day_of_week"] < 0 or values["day_of_week"] > 6:
        raise ValueError("day_of_week must be between 0 and 6")

    return values


def validate_day_of_month(cls, values):
    if "day_of_month" not in values or values["day_of_month"] is None:
        raise ValueError("day_of_month is required for monthly tasks")

    if values["day_of_month"] < 1 or values["day_of_month"] > 31:
        raise ValueError("day_of_month must be between 1 and 31")

    return values


def validate_task_types(cls, values):
    task_type = values.get("task_type")
    if task_type == "SINGLE" and not values.get("single_task"):
        raise ValueError("single_task is required for SINGLE task type")
    if task_type == "RECURRING" and not values.get("recurring_task"):
        raise ValueError("recurring_task is required for RECURRING task type")
    return values
