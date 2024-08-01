from django.db import IntegrityError
from ninja.errors import HttpError


def handle_custom_user_integrity_error(e: IntegrityError):
    if "username" in str(e):
        raise HttpError(400, "Username already in use.")
    elif "email" in str(e):
        raise HttpError(400, "Email already in use.")
    else:
        raise HttpError(400, "Invalid data.")
