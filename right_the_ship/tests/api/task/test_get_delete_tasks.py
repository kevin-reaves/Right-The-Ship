import json
from unittest.mock import patch

from django.test import TestCase

from right_the_ship.core.api.task import create_task, get_task, delete_task
from right_the_ship.core.models import CustomUser, Task, RecurringTask
from right_the_ship.core.schemas import TaskInSchema


class TestGetDeleteTask(TestCase):
    single_task = {
        "title": "Single Task",
        "description": "Single Task Description",
        "due_date": "2021-01-01",
        "completed": False,
    }

    recurring_task = {
        "title": "Recurring Task",
        "description": "Recurring Task Description",
        "completed": False,
        "frequency": "daily",
        "start_date": "2021-01-01",
        "end_date": "2021-01-31",
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
        elif model == Frequency:
            return Frequency.objects.get(*args, **kwargs)
        else:
            raise ValueError("Unknown model")

    def test_get_single_task(self):
        self.single_task["user_id"] = self.user.id
        response = create_task(None, TaskInSchema(**self.single_task))
        task_id = response.dict()["task"]["id"]

        response = get_task(None, task_id)
        response_data = response.dict()

        assert response_data["task"]["title"] == self.single_task["title"]
        assert response_data["task"]["description"] == self.single_task["description"]
        assert str(response_data["task"]["due_date"]) == self.single_task["due_date"]
        assert response_data["task"]["completed"] == self.single_task["completed"]
        assert response_data["is_recurring"] is False
        assert response_data["frequency"] is None
        assert response_data["start_date"] is None
        assert response_data["end_date"] is None

    def test_get_recurring_task(self):
        self.recurring_task["user_id"] = self.user.id
        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        response = get_task(None, task_id)
        response_data = response.dict()

        assert response_data["task"]["title"] == self.recurring_task["title"]
        assert (
            response_data["task"]["description"] == self.recurring_task["description"]
        )
        assert response_data["task"]["completed"] == self.recurring_task["completed"]
        assert response_data["is_recurring"] is True
        assert response_data["frequency"] == self.recurring_task["frequency"]
        assert str(response_data["start_date"]) == self.recurring_task["start_date"]
        assert str(response_data["end_date"]) == self.recurring_task["end_date"]

    def test_delete_single_task(self):
        self.single_task["user_id"] = self.user.id
        response = create_task(None, TaskInSchema(**self.single_task))
        task_id = response.dict()["task"]["id"]

        response = delete_task(None, task_id)
        response_data = json.loads(response.content)

        assert response_data["success"] is True
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)

    def test_delete_recurring_task(self):
        self.recurring_task["user_id"] = self.user.id
        response = create_task(None, TaskInSchema(**self.recurring_task))
        task_id = response.dict()["task"]["id"]

        response = delete_task(None, task_id)
        response_data = json.loads(response.content)

        assert response_data["success"] is True
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)
