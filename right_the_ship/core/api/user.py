from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from right_the_ship.core.schemas.user import UserOut, UserUpdateIn, UserIn

router = Router()


@router.post("/", response=UserOut)
def create_user(request, data: UserIn):
    try:
        user = User.objects.create_user(**data.dict())
        return JsonResponse(
            UserOut(id=user.id, username=user.username, email=user.email).dict()
        )
    except IntegrityError:
        raise HttpError(400, "That username is already taken")


@router.get("/{user_id}/", response=UserOut)
def get_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return JsonResponse(
        UserOut(id=user.id, username=user.username, email=user.email).dict()
    )


def update_user(request, user_id: int, data: UserUpdateIn):
    user = get_object_or_404(User, id=user_id)

    if (
        data.username
        and User.objects.filter(username=data.username).exclude(id=user_id).exists()
    ):
        raise Http404("Username already in use.")

    for attr, value in data.dict(exclude_unset=True).items():
        setattr(user, attr, value)
    user.save()

    return JsonResponse(
        UserOut(id=user.id, username=user.username, email=user.email).dict()
    )


@router.delete("/{user_id}/")
def delete_user(request, user_id: int):
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({"success": True})
    except Http404:
        raise HttpError(404, "User not found")
