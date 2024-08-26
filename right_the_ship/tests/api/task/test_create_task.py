from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from right_the_ship.core.api.task import create_task
from right_the_ship.core.models import CustomUser, Task, RecurringTask
from right_the_ship.core.schemas import TaskInSchema


class TestCreateTask(TestCase):
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

        self.user = CustomUser.objects.get_or_create(
            username="testuser", password="password"
        )[0]
        self.frequency = RecurringTask.DAILY

    def test_create_single_task(self):
        self.mock_get_object_or_404.return_value = self.user

        self.single_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.single_task))
        response_data = response.dict()

        task = Task.objects.get(title=self.single_task["title"])

        assert response_data["task"]["title"] == self.single_task["title"]
        assert response_data["task"]["description"] == self.single_task["description"]
        assert str(response_data["task"]["due_date"]) == self.single_task["due_date"]
        assert response_data["task"]["completed"] == self.single_task["completed"]
        assert response_data["is_recurring"] is False
        assert response_data["frequency"] is None
        assert response_data["start_date"] is None
        assert response_data["end_date"] is None

    def test_create_recurring_task(self):
        self.mock_get_object_or_404.return_value = self.user

        self.recurring_task["user_id"] = self.user.id

        response = create_task(None, TaskInSchema(**self.recurring_task))
        response_data = response.dict()

        task = Task.objects.get(title=self.recurring_task["title"])
        recurring_task = RecurringTask.objects.get(task=task)

        assert response_data["task"]["title"] == self.recurring_task["title"]
        assert (
            response_data["task"]["description"] == self.recurring_task["description"]
        )
        assert response_data["task"]["completed"] == self.recurring_task["completed"]
        assert response_data["is_recurring"] is True
        assert response_data["frequency"] == self.recurring_task["frequency"]
        assert str(response_data["start_date"]) == self.recurring_task["start_date"]
        assert str(response_data["end_date"]) == self.recurring_task["end_date"]

    def test_create_task_user_not_found(self):
        self.mock_get_object_or_404.side_effect = CustomUser.DoesNotExist

        self.single_task["user_id"] = "999"

        with self.assertRaises(CustomUser.DoesNotExist):
            create_task(None, TaskInSchema(**self.single_task))

    def test_create_task_frequency_not_found(self):
        self.mock_get_object_or_404.return_value = self.user

        self.recurring_task["user_id"] = self.user.id

        self.recurring_task["frequency"] = "invalid"
        with self.assertRaises(ValidationError):
            create_task(None, TaskInSchema(**self.recurring_task))

    def test_create_task_start_date_invalid_format(self):
        self.mock_get_object_or_404.return_value = self.user

        invalid_start_date = self.recurring_task.copy()
        invalid_start_date["start_date"] = "13-01-2021"

        with self.assertRaises(ValueError):
            create_task(None, TaskInSchema(**invalid_start_date))

    def test_create_task_end_date_invalid_format(self):
        self.mock_get_object_or_404.return_value = self.user

        invalid_end_date = self.recurring_task.copy()
        invalid_end_date["end_date"] = "13-01-2021"

        with self.assertRaises(ValueError):
            create_task(None, TaskInSchema(**invalid_end_date))

    def test_create_task_end_date_before_start_date(self):
        self.mock_get_object_or_404.return_value = self.user

        invalid_end_date = self.recurring_task.copy()
        invalid_end_date["start_date"] = "2021-01-31"
        invalid_end_date["end_date"] = "2021-01-01"

        with self.assertRaises(ValidationError):
            create_task(None, TaskInSchema(**invalid_end_date))

    def test_create_task_end_date_before_start_date(self):
        self.mock_get_object_or_404.return_value = self.user
        invalid_end_date = self.recurring_task.copy()
        invalid_end_date["user_id"] = self.user.id
        invalid_end_date["start_date"] = "2021-01-31"
        invalid_end_date["end_date"] = "2021-01-01"

        with self.assertRaises(ValidationError):
            create_task(None, TaskInSchema(**invalid_end_date))

    def test_create_task_without_due_date(self):
        self.mock_get_object_or_404.return_value = self.user
        task_without_due_date = self.single_task.copy()
        task_without_due_date["user_id"] = self.user.id
        task_without_due_date.pop("due_date")

        response = create_task(None, TaskInSchema(**task_without_due_date))
        response_data = response.dict()

        task = Task.objects.get(title=task_without_due_date["title"])

        assert response_data["task"]["title"] == task_without_due_date["title"]
        assert (
            response_data["task"]["description"] == task_without_due_date["description"]
        )
        assert response_data["task"]["due_date"] is None
        assert response_data["task"]["completed"] == task_without_due_date["completed"]
        assert response_data["is_recurring"] is False
        assert response_data["frequency"] is None
        assert response_data["start_date"] is None
        assert response_data["end_date"] is None

    def test_create_recurring_task_without_end_date(self):
        self.mock_get_object_or_404.return_value = self.user
        task_without_end_date = self.recurring_task.copy()
        task_without_end_date["user_id"] = self.user.id
        task_without_end_date.pop("end_date")

        response = create_task(None, TaskInSchema(**task_without_end_date))
        response_data = response.dict()

        task = Task.objects.get(title=task_without_end_date["title"])
        recurring_task = RecurringTask.objects.get(task=task)

        assert response_data["task"]["title"] == task_without_end_date["title"]
        assert (
            response_data["task"]["description"] == task_without_end_date["description"]
        )
        assert response_data["task"]["completed"] == task_without_end_date["completed"]
        assert response_data["is_recurring"] is True
        assert response_data["frequency"] == task_without_end_date["frequency"]
        assert str(response_data["start_date"]) == task_without_end_date["start_date"]
        assert response_data["end_date"] is None
