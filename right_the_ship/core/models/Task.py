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
    MONTHLY = "monthly"
    YEARLY = "yearly"

    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
        (YEARLY, "Yearly"),
    ]

    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.task.title} - {self.get_frequency_display()}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")

        self.frequency = self.frequency.lower()
        if self.frequency not in dict(self.FREQUENCY_CHOICES).keys():
            raise ValidationError("Invalid frequency")

        if self.frequency in [self.WEEKLY, self.MONTHLY] and not self.day:
            raise ValidationError("Day is required for weekly and monthly tasks")

        if self.frequency in [self.DAILY] and self.day:
            raise ValidationError("Day will be ignored for daily tasks")

        if self.frequency == self.WEEKLY and (self.day < 1 or self.day > 7):
            raise ValidationError("Day must be between 1 and 7 for weekly tasks")

        if self.frequency == self.MONTHLY and (self.day < 1 or self.day > 31):
            raise ValidationError("Day must be between 1 and 31 for monthly tasks")

        if self.frequency == self.YEARLY and (self.day < 1 or self.day > 366):
            raise ValidationError("Day must be between 1 and 366 for yearly tasks")

    def save(self, *args, **kwargs):
        self.clean()
        super(RecurringTask, self).save(*args, **kwargs)


class SingleTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.task.title
