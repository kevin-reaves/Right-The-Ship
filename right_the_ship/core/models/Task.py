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


class Frequency(models.Model):
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

    name = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

    def clean(self):
        if self.name not in dict(self.FREQUENCY_CHOICES):
            raise ValidationError(f"{self.name} is not a valid frequency")

    def save(self, *args, **kwargs):
        self.clean()
        if not Frequency.objects.filter(name=self.name).exists():
            super(Frequency, self).save(*args, **kwargs)


class RecurringTask(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    frequency = models.ForeignKey(Frequency, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.task.title} - {self.frequency.get_name_display()}"

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
