from django.contrib import admin

from right_the_ship.core.models.task import (
    Task,
    WeeklyRecurrence,
    MonthlyRecurrence,
    SingleTask,
    RecurringTask,
)


class WeeklyRecurrenceInline(admin.TabularInline):
    model = WeeklyRecurrence
    extra = 1


class MonthlyRecurrenceInline(admin.TabularInline):
    model = MonthlyRecurrence
    extra = 1


class RecurringTaskAdmin(admin.ModelAdmin):
    inlines = [WeeklyRecurrenceInline, MonthlyRecurrenceInline]


admin.site.register(SingleTask)

admin.site.register(RecurringTask, RecurringTaskAdmin)
