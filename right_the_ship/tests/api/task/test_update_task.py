from django.test import TestCase
from unittest.mock import patch
from right_the_ship.core.api.task import update_task, create_task
from django.core.exceptions import ValidationError

from right_the_ship.core.models import CustomUser, Task, RecurringTask
from right_the_ship.core.schemas import TaskInSchema


class TestUpdateTask(TestCase):
    single_task = {
        "title": "Single Task",
        "description": "Single Task Description",
        "due_date": "2021-01-01",
        "completed": False,
    }

    updated_single_task = {
        "title": "Updated Single Task",
        "description": "Updated Single Task Description",
        "due_date": "2021-02-01",
        "completed": True,
    }

    recurring_task = {
        "title": "Recurring Task",
        "description": "Recurring Task Description",
        "completed": False,
        "frequency": "daily",
        "start_date": "2021-01-01",
        "end_date": "2021-01-31",
    }

    updated_recurring_task = {
        "title": "Updated Recurring Task",
        "description": "Updated Recurring Task Description",
        "completed": True,
        "frequency": "weekly",
        "start_date": "2021-02-01",
        "end_date": "2021-03-01",
        "day": 5,
    }

    def setUp(self):
        self.patcher_get_object_or_404 = patch(
            "right_the_ship.core.api.task.get_object_or_404"
        )
        self.mock_get_object_or_404 = self.patcher_get_object_or_404.start()
        self.addCleanup(self.patcher_get_object_or_404.stop)

        self.user = CustomUser.objects.create(username="testuser", password="password")
        self.frequency_daily = RecurringTask.DAILY
        self.frequency_weekly = RecurringTask.WEEKLY

        self.mock_get_object_or_404.side_effect = (
            self.mock_get_object_or_404_side_effect
        )

    def mock_get_object_or_404_side_effect(self, model, *args, **kwargs):
        if model == CustomUser:
            return self.user
        elif model == Task:
            return Task.objects.get(*args, **kwargs)
        elif model == RecurringTask:
            return RecurringTask.objects.get(*args, **kwargs)
        else:
            raise ValueError("Unknown model")

    def test_update_recurring_task(self):
        self.recurring_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        updated_data = self.updated_recurring_task.copy()
        updated_data["user_id"] = self.user.id

        response = update_task(None, task_id, TaskInSchema(**updated_data))
        response_data = response.dict()

        updated_task = Task.objects.get(id=task_id)
        updated_recurring_task = RecurringTask.objects.get(task=updated_task)

        assert response_data["task"]["title"] == updated_data["title"]
        assert response_data["task"]["description"] == updated_data["description"]
        assert response_data["task"]["completed"] == updated_data["completed"]
        assert response_data["is_recurring"] is True
        assert response_data["frequency"] == updated_data["frequency"]
        assert str(response_data["start_date"]) == updated_data["start_date"]
        assert str(response_data["end_date"]) == updated_data["end_date"]

    def test_update_task_user_not_found(self):
        self.single_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.single_task))
        task_id = response.dict()["task"]["id"]

        updated_data = self.updated_single_task.copy()
        updated_data["user_id"] = "999"

        self.mock_get_object_or_404.side_effect = CustomUser.DoesNotExist

        with self.assertRaises(CustomUser.DoesNotExist):
            update_task(None, task_id, TaskInSchema(**updated_data))

    def test_update_task_frequency_not_found(self):
        self.recurring_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        updated_data = self.updated_recurring_task.copy()
        updated_data["user_id"] = self.user.id
        updated_data["frequency"] = "invalid"

        with self.assertRaises(ValidationError):
            update_task(None, task_id, TaskInSchema(**updated_data))

    def test_update_task_start_date_invalid_format(self):
        self.recurring_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        updated_data = self.updated_recurring_task.copy()
        updated_data["user_id"] = self.user.id
        updated_data["start_date"] = "13-01-2021"

        with self.assertRaises(ValueError):
            update_task(None, task_id, TaskInSchema(**updated_data))

    def test_update_task_end_date_invalid_format(self):
        self.recurring_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        updated_data = self.updated_recurring_task.copy()
        updated_data["user_id"] = self.user.id
        updated_data["end_date"] = "13-01-2021"

        with self.assertRaises(ValueError):
            update_task(None, task_id, TaskInSchema(**updated_data))

    def test_update_task_end_date_before_start_date(self):
        self.recurring_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        updated_data = self.updated_recurring_task.copy()
        updated_data["user_id"] = self.user.id
        updated_data["start_date"] = "2021-03-01"
        updated_data["end_date"] = "2021-02-01"

        with self.assertRaises(ValidationError):
            update_task(None, task_id, TaskInSchema(**updated_data))
