# Generated by Django 5.0.7 on 2024-08-06 01:23

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Frequency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("biweekly", "Biweekly"),
                            ("monthly", "Monthly"),
                            ("bimonthly", "Bimonthly"),
                            ("yearly", "Yearly"),
                        ],
                        max_length=10,
                        unique=True,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="customuser",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customuser",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, null=True)),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                ("completed", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.customuser",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SingleTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.task"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecurringTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField(default=django.utils.timezone.now)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "frequency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.frequency"
                    ),
                ),
                (
                    "task",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="core.task"
                    ),
                ),
            ],
        ),
    ]
