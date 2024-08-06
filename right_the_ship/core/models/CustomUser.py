from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from right_the_ship.core.mixins.SoftDelete import SoftDeleteMixin
from right_the_ship.core.mixins.Timestamp import TimestampMixin


class CustomUser(AbstractUser, TimestampMixin, SoftDeleteMixin):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
