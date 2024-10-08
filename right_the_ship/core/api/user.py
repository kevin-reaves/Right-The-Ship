from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from right_the_ship.core.models.CustomUser import CustomUser
from right_the_ship.core.schemas.user import UserOut, UserUpdateIn, UserIn
from right_the_ship.core.utils.handle_custom_user_integrity_error import (
    handle_custom_user_integrity_error,
)

router = Router()


@router.post("/", response=UserOut)
def create_user(request, data: UserIn):
    try:
        user = CustomUser.objects.create_user(**data.dict())
        user.save()
        return JsonResponse(
            UserOut(id=user.id, username=user.username, email=user.email).dict()
        )
    except IntegrityError as e:
        handle_custom_user_integrity_error(e)


@router.get("/{user_id}/", response=UserOut)
def get_user(request, user_id: int):
    user = get_object_or_404(CustomUser, id=user_id)
    return JsonResponse(
        UserOut(id=user.id, username=user.username, email=user.email).dict()
    )


@router.patch("/{user_id}/", response=UserOut)
def update_user(request, user_id: int, data: UserUpdateIn):
    user = get_object_or_404(CustomUser, id=user_id)
    try:
        # Filter out username or other unique fields if not provided
        for key, value in data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        user.save()
        return JsonResponse(
            UserOut(id=user.id, username=user.username, email=user.email).dict()
        )
    except IntegrityError as e:
        handle_custom_user_integrity_error(e)


@router.delete("/{user_id}/")
def delete_user(request, user_id: int):
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({"success": True})
    except Http404:
        raise HttpError(404, "User not found")
