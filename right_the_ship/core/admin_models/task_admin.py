from django.contrib import admin
from right_the_ship.core.models import Task, RecurringTask, SingleTask


class RecurringTaskInline(admin.StackedInline):
    model = RecurringTask
    extra = 0  # Removes the extra empty inline form


class SingleTaskInline(admin.StackedInline):
    model = SingleTask
    extra = 0  # Removes the extra empty inline form


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "due_date", "completed")
    list_filter = ("completed", "due_date", "user")
    search_fields = ("title", "description", "user__username")
    date_hierarchy = "due_date"
    ordering = ("due_date",)
    inlines = [RecurringTaskInline, SingleTaskInline]
