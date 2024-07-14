import json
import unittest
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import Http404
from ninja.errors import HttpError
from pydantic import ValidationError

from right_the_ship.core.api.user import update_user, create_user, get_user, delete_user
from right_the_ship.core.schemas.user import UserUpdateIn, UserIn


class TestUser(unittest.TestCase):
    def setUp(self):
        self.patcher_get_object_or_404 = patch(
            "right_the_ship.core.api.user.get_object_or_404"
        )
        self.patcher_user_save = patch(
            "django.contrib.auth.models.User.save", autospec=True
        )
        self.patcher_create_user = patch(
            "right_the_ship.core.api.user.User.objects.create_user"
        )

        self.mock_get_object_or_404 = self.patcher_get_object_or_404.start()
        self.mock_user_save = self.patcher_user_save.start()
        self.mock_create_user = self.patcher_create_user.start()

        self.addCleanup(self.patcher_get_object_or_404.stop)
        self.addCleanup(self.patcher_user_save.stop)
        self.addCleanup(self.patcher_create_user.stop)

        self.mock_user = MagicMock(spec=User)
        self.mock_user.id = 1
        self.mock_user.username = "old_username"
        self.mock_user.email = "old_email@example.com"
        self.mock_user.password = "old_password"
        self.mock_user.save = MagicMock(name="save")

    def test_update_user_without_password(self):
        self.mock_get_object_or_404.return_value = self.mock_user
        data = UserUpdateIn(username="new_username")

        response = update_user(None, 1, data)
        response_data = json.loads(response.content)

        assert self.mock_user.username == "new_username"
        assert response_data["username"] == "new_username"
        assert "password" not in response_data
        self.mock_user.save.assert_called_once_with()

    def test_update_user_with_password(self):
        self.mock_get_object_or_404.return_value = self.mock_user
        data = UserUpdateIn(username="new_username", password="new_password")

        response = update_user(None, 1, data)
        response_data = json.loads(response.content)

        assert response_data["username"] == "new_username"
        assert "password" not in response_data
        self.mock_user.save.assert_called_once_with()

    def test_cannot_update_email(self):
        self.mock_get_object_or_404.return_value = self.mock_user
        data = UserUpdateIn(username="new_username", email="new@email.com")

        response = update_user(None, 1, data)
        response_data = json.loads(response.content)

        assert response_data["username"] == "new_username"
        assert response_data["email"] == self.mock_user.email
        assert "password" not in response_data
        self.mock_user.save.assert_called_once_with()

    def test_cannot_update_non_existent_user(self):
        self.mock_get_object_or_404.side_effect = Http404

        with pytest.raises(Http404):
            update_user(None, 5, UserUpdateIn(username="new_username"))

    @patch("django.contrib.auth.models.User.objects.filter")
    def test_cannot_create_user_with_existing_username(self, mock_filter):
        existing_user = MagicMock(spec=User)
        self.mock_get_object_or_404.return_value = self.mock_user
        mock_filter.return_value.exclude.return_value.exists.return_value = True
        data = UserUpdateIn(username="existing_username")

        with pytest.raises(Http404, match="Username already in use."):
            update_user(None, 1, data)

        self.mock_user.save.assert_not_called()

    def test_cannot_create_user_with_too_short_values(self):
        self.mock_get_object_or_404.return_value = MagicMock(spec=User)

        with pytest.raises(ValidationError):
            update_user(None, 1, UserUpdateIn(username="a"))

        with pytest.raises(ValidationError):
            update_user(None, 1, UserUpdateIn(password="a"))

        with pytest.raises(ValidationError):
            update_user(None, 1, UserUpdateIn(email="a"))

    def test_cannot_create_user_with_too_long_values(self):
        self.mock_get_object_or_404.return_value = MagicMock(spec=User)

        with pytest.raises(ValidationError):
            update_user(None, 1, UserUpdateIn(username="a" * 51))

        with pytest.raises(ValidationError):
            update_user(None, 1, UserUpdateIn(password="a" * 51))

        with pytest.raises(ValidationError):
            update_user(None, 1, UserUpdateIn(email="a" * 51 + "@example.com"))

    def test_create_user_success(self):
        mock_user = MagicMock(
            id=1, username="new_username", email="new_email@example.com"
        )
        self.mock_create_user.return_value = mock_user

        data = UserIn(
            username="new_username",
            email="new_email@example.com",
            password="new_password",
        )
        response = create_user(None, data)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data["id"] == mock_user.id
        assert response_data["username"] == mock_user.username
        assert response_data["email"] == mock_user.email

    def test_create_user_integrity_error(self):
        self.mock_create_user.side_effect = IntegrityError

        data = UserIn(
            username="taken_username", email="email@example.com", password="password"
        )

        with pytest.raises(HttpError) as excinfo:
            create_user(None, data)

        assert excinfo.value.status_code == 400
        assert str(excinfo.value) == "That username is already taken"

    def test_get_user_success(self):
        self.mock_get_object_or_404.return_value = self.mock_user

        response = get_user(None, 1)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data["id"] == self.mock_user.id
        assert response_data["username"] == self.mock_user.username
        assert response_data["email"] == self.mock_user.email

    def test_get_user_not_found(self):
        self.mock_get_object_or_404.side_effect = Http404

        with pytest.raises(Http404):
            get_user(None, 999)

    def test_delete_user_success(self):
        self.mock_get_object_or_404.return_value = self.mock_user

        response = delete_user(None, 1)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data["success"] is True
        self.mock_user.delete.assert_called_once()

    def test_delete_user_not_found(self):
        self.mock_get_object_or_404.side_effect = Http404

        with pytest.raises(HttpError) as excinfo:
            delete_user(None, 999)

        assert excinfo.value.status_code == 404
