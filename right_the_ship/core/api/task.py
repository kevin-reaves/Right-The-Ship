from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Router

from right_the_ship.core.models.CustomUser import CustomUser
from right_the_ship.core.models.Task import Task, RecurringTask
from right_the_ship.core.schemas.task import TaskSchema, TaskDetailSchema, TaskInSchema

router = Router()

# TODO
"""
    Recurring tasks -> Single tasks? Or just delete the recurring task and create a new one?
    Factory for test data
    Add user authentication
"""


def generate_task_detail_schema(task: Task) -> TaskDetailSchema:
    recurring_task = getattr(task, "recurringtask", None)
    is_recurring = recurring_task is not None
    frequency = recurring_task.frequency if is_recurring else None
    start_date = recurring_task.start_date if is_recurring else None
    end_date = recurring_task.end_date if is_recurring else None

    return TaskDetailSchema(
        task=TaskSchema.from_orm(task),
        is_recurring=is_recurring,
        frequency=frequency,
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/", response=TaskDetailSchema)
def create_task(request, data: TaskInSchema):
    task_data = data.dict()
    user_id = task_data.pop("user_id")
    user = get_object_or_404(CustomUser, id=user_id)

    frequency = task_data.pop("frequency", None)
    start_date = task_data.pop("start_date", None)
    end_date = task_data.pop("end_date", None)

    task = Task.objects.create(user=user, **task_data)

    if frequency and start_date:
        RecurringTask.objects.create(
            task=task,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
        )

    return generate_task_detail_schema(task)


@router.get("/{task_id}/", response=TaskDetailSchema)
def get_task(request, task_id: int):
    task = Task.objects.get(id=task_id)
    return generate_task_detail_schema(task)


@router.delete("/{task_id}/")
def delete_task(request, task_id: int):
    task = Task.objects.get(id=task_id)
    task.delete()
    return JsonResponse({"success": True})


@router.patch("/{task_id}/", response=TaskDetailSchema)
def update_task(request, task_id: int, data: TaskInSchema):
    task_data = data.dict()
    user_id = task_data.pop("user_id")
    user = get_object_or_404(CustomUser, id=user_id)

    frequency = task_data.pop("frequency", None)
    start_date = task_data.pop("start_date", None)
    end_date = task_data.pop("end_date", None)

    task = get_object_or_404(Task, id=task_id)

    task.user = user
    for attr, value in task_data.items():
        setattr(task, attr, value)
    task.save()

    if frequency and start_date:
        RecurringTask.objects.update_or_create(
            task=task,
            defaults={
                "frequency": frequency,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

    return generate_task_detail_schema(task)
