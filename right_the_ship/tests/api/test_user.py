import json
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import Http404
from django.test import TestCase
from ninja.errors import HttpError
from pydantic import ValidationError

from right_the_ship.core.api.user import update_user, create_user, get_user, delete_user
from right_the_ship.core.schemas.user import UserUpdateIn, UserIn


class TestUser(TestCase):
    old_username = "old_username"
    old_email = "old@example.com"
    old_password = "old_password"

    new_username = "new_username"
    new_email = "new@example.com"
    new_password = "new_password"

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

    def create_mock_user(self):
        self.mock_user = MagicMock(spec=User)
        self.mock_user.id = 1
        self.mock_user.username = self.old_username
        self.mock_user.email = self.old_email
        self.mock_user.password = self.old_password
        self.mock_get_object_or_404.return_value = self.mock_user

    def test_update_user_without_password(self):
        self.create_mock_user()
        data = UserUpdateIn(username=self.new_username)

        response = update_user(None, 1, data)
        response_data = json.loads(response.content)

        assert self.mock_user.username == self.new_username
        assert response_data["username"] == self.new_username
        assert "password" not in response_data
        self.mock_user.save.assert_called_once_with()

    def test_update_user_with_password(self):
        self.create_mock_user()
        data = UserUpdateIn(username=self.new_username, password=self.new_password)

        response = update_user(None, 1, data)
        response_data = json.loads(response.content)

        assert response_data["username"] == self.new_username
        assert "password" not in response_data
        self.mock_user.save.assert_called_once_with()

    def test_cannot_update_email(self):
        self.create_mock_user()
        data = UserUpdateIn(username=self.new_username, email=self.new_email)

        response = update_user(None, 1, data)
        response_data = json.loads(response.content)

        assert response_data["username"] == self.new_username
        assert response_data["email"] == self.mock_user.email
        assert "password" not in response_data
        self.mock_user.save.assert_called_once_with()

    def test_cannot_update_non_existent_user(self):
        self.mock_get_object_or_404.side_effect = Http404

        with pytest.raises(Http404):
            update_user(None, 5, UserUpdateIn(username=self.new_username))

    def test_cannot_create_user_with_existing_username(self):
        self.patcher_create_user.stop()
        self.patcher_user_save.stop()

        data = UserIn(
            username=self.old_username, password=self.old_password, email=self.old_email
        )
        create_user(None, data)

        data.email = self.new_email

        with pytest.raises(HttpError) as excinfo:
            create_user(None, data)

        assert "username" in excinfo.value.message.lower()

    def test_cannot_create_user_with_existing_email(self):
        self.patcher_create_user.stop()
        self.patcher_user_save.stop()

        data = UserIn(
            username=self.old_username, password=self.old_password, email=self.old_email
        )
        create_user(None, data)

        data.username = self.new_username

        with pytest.raises(HttpError) as excinfo:
            create_user(None, data)

        assert "email" in excinfo.value.message.lower()

    def test_cannot_create_user_with_too_short_values(self):
        self.create_mock_user()
        self.mock_get_object_or_404.return_value = MagicMock(spec=User)

        with pytest.raises(ValidationError):
            create_user(
                None,
                UserIn(username="a", password=self.old_password, email=self.old_email),
            )

        with pytest.raises(ValidationError):
            create_user(
                None,
                UserIn(password="a", username=self.old_username, email=self.old_email),
            )

        with pytest.raises(ValidationError):
            create_user(
                None,
                UserIn(
                    email="a", username=self.old_username, password=self.old_password
                ),
            )

    def test_cannot_create_user_with_too_long_values(self):
        self.create_mock_user()
        self.mock_get_object_or_404.return_value = MagicMock(spec=User)

        with pytest.raises(ValidationError):
            create_user(
                None,
                UserIn(
                    username="a" * 51, password=self.old_password, email=self.old_email
                ),
            )

        with pytest.raises(ValidationError):
            create_user(
                None,
                UserIn(
                    password="a" * 51, username=self.old_username, email=self.old_email
                ),
            )

        with pytest.raises(ValidationError):
            create_user(
                None,
                UserIn(
                    email="a" * 51 + "@example.com",
                    username=self.old_username,
                    password=self.old_password,
                ),
            )

    def test_get_user_success(self):
        self.create_mock_user()

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
        self.create_mock_user()
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

    def test_update_user_with_integrity_error_throws(self):
        self.create_mock_user()
        self.mock_user.save.side_effect = IntegrityError

        with pytest.raises(HttpError):
            update_user(None, 1, UserUpdateIn(username=self.new_username))
