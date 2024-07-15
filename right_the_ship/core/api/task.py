from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import Router

from right_the_ship.core.models.task import (
    Task,
    SingleTask,
    RecurringTask,
    WeeklyRecurrence,
    MonthlyRecurrence,
    BiweeklyRecurrence,
    DailyRecurrence,
)
from right_the_ship.core.schemas.task import TaskIn, TaskUpdateIn

router = Router()


@router.post("/")
def create_task(request, task_data: TaskIn):
    user = get_object_or_404(User, id=task_data.user_id)

    if task_data.task_type == "SINGLE":
        single_task_data = task_data.single_task.dict()

        single_task = SingleTask(
            user=user,
            title=task_data.title,
            description=task_data.description,
            end_date=single_task_data["end_date"],
        )

        single_task.save()

        task = Task(
            user=user,
            title=task_data.title,
            description=task_data.description,
            task_type="SINGLE",
            start_date=task_data.start_date,
            single_task=single_task,
        )

    elif task_data.task_type == "RECURRING":
        daily_recurrences = []
        weekly_recurrences = []
        biweekly_recurrences = []
        monthly_recurrences = []

        recurring_task_data = task_data.recurring_task.dict()

        recurring_task = RecurringTask(
            user=user,
            title=task_data.title,
            description=task_data.description,
            start_date=task_data.start_date,
            end_date=recurring_task_data["end_date"],
        )

        if recurring_task_data.get("days_of_week"):
            for day in recurring_task_data["days_of_week"]:
                match recurring_task_data["frequency"]:
                    case "DAILY":
                        recurrence = DailyRecurrence(task=recurring_task)
                        daily_recurrences.append(recurrence)
                    case "WEEKLY":
                        recurrence = WeeklyRecurrence(
                            task=recurring_task, day_of_week=day["day_of_week"]
                        )
                        weekly_recurrences.append(recurrence)
                    case "BIWEEKLY":
                        recurrence = BiweeklyRecurrence(
                            task=recurring_task, day_of_week=day["day_of_week"]
                        )
                        biweekly_recurrences.append(recurrence)
                    case "MONTHLY":
                        recurrence = MonthlyRecurrence(
                            task=recurring_task, day_of_month=day["day_of_month"]
                        )
                        monthly_recurrences.append(recurrence)
                    case _:
                        raise ValueError("Invalid frequency")

                recurring_task.save()
                recurrence.save()

        if recurring_task_data.get("days_of_month"):
            for day in recurring_task_data["days_of_month"]:
                recurrence = MonthlyRecurrence(
                    task=recurring_task, day_of_month=day["day_of_month"]
                )
                monthly_recurrences.append(recurrence)
                recurring_task.save()
                recurrence.save()

        task = Task(
            user=user,
            title=task_data.title,
            description=task_data.description,
            task_type="RECURRING",
            recurring_task=recurring_task,
        )

        recurring_task.save()

    else:
        raise ValueError("Invalid task type")

    task.save()
    return task.dict()


@router.get("/{task_id}/")
def get_task(request, task_id: int):
    task = Task.objects.get(id=task_id)
    return task.dict()


def delete_existing_recurrences(task):
    task.recurring_task.dailyrecurrence_set.all().delete()
    task.recurring_task.weeklyrecurrence_set.all().delete()
    task.recurring_task.biweeklyrecurrence_set.all().delete()
    task.recurring_task.monthlyrecurrence_set.all().delete()


@router.patch("/{task_id}/")
def update_task(request, task_id: int, task_data: TaskUpdateIn):
    task = Task.objects.get(id=task_id)

    single_task_data = (
        task_data.single_task.dict(exclude_unset=True)
        if task_data.single_task
        else None
    )
    recurring_task_data = (
        task_data.recurring_task.dict(exclude_unset=True)
        if task_data.recurring_task
        else None
    )

    if task_data.title:
        task.title = task_data.title
    if task_data.description:
        task.description = task_data.description
    if task_data.start_date:
        task.start_date = task_data.start_date

    if task_data.single_task:
        if task.recurring_task:
            task.recurring_task.delete()
            task.recurring_task = None

        if not task.single_task:
            task.single_task = SingleTask(user=task.user)

        task.single_task.end_date = single_task_data["end_date"]
        task.task_type = "SINGLE"

    elif task_data.recurring_task:
        delete_existing_recurrences(task)

        if task.single_task:
            task.single_task.delete()
            task.single_task = None

        if not task.recurring_task:
            task.recurring_task = RecurringTask(user=task.user)

        task.recurring_task.end_date = recurring_task_data["end_date"]

        if recurring_task_data.get("days_of_week"):
            for day in recurring_task_data["days_of_week"]:
                match recurring_task_data["frequency"]:
                    case "DAILY":
                        recurrence = DailyRecurrence(task=task.recurring_task)
                    case "WEEKLY":
                        recurrence = WeeklyRecurrence(
                            task=task.recurring_task, day_of_week=day["day_of_week"]
                        )
                    case "BIWEEKLY":
                        recurrence = BiweeklyRecurrence(
                            task=task.recurring_task, day_of_week=day["day_of_week"]
                        )
                    case "MONTHLY":
                        recurrence = MonthlyRecurrence(
                            task=task.recurring_task, day_of_month=day["day_of_month"]
                        )
                    case _:
                        raise ValueError("Invalid frequency")

                recurrence.save()
        elif recurring_task_data.get("days_of_month"):
            for day in recurring_task_data["days_of_month"]:
                recurrence = MonthlyRecurrence(
                    task=task.recurring_task, day_of_month=day["day_of_month"]
                )
                recurrence.save()

            task.recurring_task.save()

    task.save()
    return task.dict()


@router.delete("/{task_id}/")
def delete_task(request, task_id: int):
    task = Task.objects.get(id=task_id)
    task.delete()
    return {"success": True}
