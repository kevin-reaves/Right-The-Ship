from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from right_the_ship.core.mixins.SoftDelete import SoftDeleteMixin
from right_the_ship.core.mixins.Timestamp import TimestampMixin
from right_the_ship.core.models.CustomUser import CustomUser


class Task(TimestampMixin, SoftDeleteMixin):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class RecurringTask(models.Model):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"
    YEARLY = "yearly"

    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (BIWEEKLY, "Biweekly"),
        (MONTHLY, "Monthly"),
        (BIMONTHLY, "Bimonthly"),
        (YEARLY, "Yearly"),
    ]

    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.task.title} - {self.get_frequency_display()}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")

    def save(self, *args, **kwargs):
        self.clean()
        super(RecurringTask, self).save(*args, **kwargs)


class SingleTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.task.title
