from django.db.models.signals import post_migrate
from django.core.management import call_command
from django.apps import apps


def create_superuser(sender, **kwargs):
    call_command("create_superuser")


def setup_signals():
    post_migrate.connect(create_superuser, sender=apps.get_app_config("core"))
