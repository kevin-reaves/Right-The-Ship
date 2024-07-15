import calendar

from django.db import models
from django.contrib.auth.models import User
from datetime import date


class BaseTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=date.today)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class SingleTask(BaseTask):
    end_date = models.DateField()

    def is_due(self):
        return date.today() == self.end_date

    def dict(self):
        return {
            "end_date": self.end_date,
        }


class RecurringTask(BaseTask):
    FREQUENCY_CHOICES = [
        ("DAILY", "Daily Task"),
        ("WEEKLY", "Weekly Task"),
        ("TWICE_WEEKLY", "Twice Weekly Task"),
        ("BIWEEKLY", "Biweekly Task (every two weeks)"),
        ("MONTHLY", "Monthly Task"),
    ]

    frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES)
    end_date = models.DateField()

    def is_due(self):
        today = date.today()

        if self.frequency == "DAILY":
            return self.start_date <= today <= self.end_date

        if self.frequency in {"WEEKLY", "TWICE_WEEKLY"}:
            recurrence_days = self.weeklyrecurrence_set.all()
            return (self.start_date <= today <= self.end_date) and any(
                today.weekday() == day.day_of_week for day in recurrence_days
            )

        if self.frequency == "BIWEEKLY":
            recurrence_days = self.biweeklyrecurrence_set.all()
            return (self.start_date <= today <= self.end_date) and any(
                (today - self.start_date).days % 14 == 0
                and today.weekday() == day.day_of_week
                for day in recurrence_days
            )

        if self.frequency == "MONTHLY":
            recurrence_days = self.monthlyrecurrence_set.all()
            return (self.start_date <= today <= self.end_date) and any(
                today.day
                == self.get_adjusted_day(today.year, today.month, day.day_of_month)
                for day in recurrence_days
            )

        return False

    def get_adjusted_day(self, year, month, day_of_month):
        """Adjusts the day_of_month to the last valid day of the month if necessary."""
        last_day_of_month = calendar.monthrange(year, month)[1]
        return min(day_of_month, last_day_of_month)

    def dict(self):
        return_dict = {
            "task_type": self.frequency,
            "end_date": self.end_date,
            "weekly_recurrences": [
                {"day_of_week": day.day_of_week}
                for day in self.weeklyrecurrence_set.all()
            ],
            "biweekly_recurrences": [
                {"day_of_week": day.day_of_week}
                for day in self.biweeklyrecurrence_set.all()
            ],
            "monthly_recurrences": [
                {"day_of_month": day.day_of_month}
                for day in self.monthlyrecurrence_set.all()
            ],
        }

        # exclude empty lists
        return {k: v for k, v in return_dict.items() if v}


class DailyRecurrence(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE)


class WeeklyRecurrence(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()  # 0 = Monday, 6 = Sunday


class BiweeklyRecurrence(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()  # 0 = Monday, 6 = Sunday


class MonthlyRecurrence(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE)
    day_of_month = models.IntegerField()  # 1 to 31


class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ("SINGLE", "Single Task"),
        ("RECURRING", "Recurring Task"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES)
    start_date = models.DateField(default=date.today)
    single_task = models.OneToOneField(
        SingleTask, on_delete=models.CASCADE, blank=True, null=True
    )
    recurring_task = models.OneToOneField(
        RecurringTask, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.title

    def is_due(self):
        if self.task_type == "SINGLE" and self.single_task:
            return self.single_task.is_due()
        elif self.task_type == "RECURRING" and self.recurring_task:
            return self.recurring_task.is_due()
        return False

    def dict(self):
        return_data = {
            "id": self.id,
            "user_id": self.user.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "start_date": self.start_date,
        }

        if self.single_task:
            return_data["single_task"] = self.single_task.dict()

        if self.recurring_task:
            return_data["recurring_task"] = self.recurring_task.dict()

        return return_data
