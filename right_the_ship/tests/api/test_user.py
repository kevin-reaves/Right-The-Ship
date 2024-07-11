import json

import pytest
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.http import Http404
from pydantic import ValidationError

from right_the_ship.core.api.user import update_user
from right_the_ship.core.schemas.user import UserUpdateIn


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "old_username"
    user.email = "old_email@example.com"
    user.password = "old_password"
    user.save = MagicMock(name='save')
    return user


@patch('right_the_ship.core.api.user.get_object_or_404')
@patch('django.contrib.auth.models.User.save', autospec=True)
def test_update_user_without_password(mock_save, mock_get_object_or_404, mock_user):
    mock_get_object_or_404.return_value = mock_user
    data = UserUpdateIn(username="new_username")

    response = update_user(None, 1, data)
    response_data = json.loads(response.content)

    assert mock_user.username == "new_username"
    assert response_data['username'] == "new_username"
    assert 'password' not in response_data
    mock_user.save.assert_called_once_with()


@patch('right_the_ship.core.api.user.get_object_or_404')
@patch('django.contrib.auth.models.User.save', autospec=True)
def test_update_user_with_password(mock_save, mock_get_object_or_404, mock_user):
    mock_get_object_or_404.return_value = mock_user
    data = UserUpdateIn(username="new_username", password="new_password")

    response = update_user(None, 1, data)
    response_data = json.loads(response.content)

    assert response_data['username'] == "new_username"
    assert 'password' not in response_data
    mock_user.save.assert_called_once_with()


@patch('right_the_ship.core.api.user.get_object_or_404')
@patch('django.contrib.auth.models.User.save', autospec=True)
def test_cannot_update_email(mock_save, mock_get_object_or_404, mock_user):
    mock_get_object_or_404.return_value = mock_user
    data = UserUpdateIn(username="new_username", email="new@email.com")

    response = update_user(None, 1, data)
    response_data = json.loads(response.content)

    assert response_data['username'] == "new_username"
    assert response_data['email'] == mock_user.email
    assert 'password' not in response_data
    mock_user.save.assert_called_once_with()


@patch('right_the_ship.core.api.user.get_object_or_404')
def test_cannot_update_non_existent_user(mock_get_object_or_404):
    mock_get_object_or_404.side_effect = Http404

    with pytest.raises(Http404):
        update_user(None, 5, UserUpdateIn(username="new_username"))


@patch('right_the_ship.core.api.user.get_object_or_404')
@patch('django.contrib.auth.models.User.objects.filter')
def test_cannot_create_user_with_existing_username(mock_filter, mock_get_object_or_404, mock_user):
    existing_user = MagicMock(spec=User)
    mock_get_object_or_404.return_value = mock_user
    mock_filter.return_value.exclude.return_value.exists.return_value = True
    data = UserUpdateIn(username="existing_username")

    with pytest.raises(Http404, match="Username already in use."):
        update_user(None, 1, data)

    mock_user.save.assert_not_called()


@patch('right_the_ship.core.api.user.get_object_or_404')
def test_cannot_create_user_with_too_short_values(mock_get_object_or_404):
    mock_get_object_or_404.return_value = MagicMock(spec=User)

    with pytest.raises(ValidationError):
        update_user(None, 1, UserUpdateIn(username="a"))

    with pytest.raises(ValidationError):
        update_user(None, 1, UserUpdateIn(password="a"))

    with pytest.raises(ValidationError):
        update_user(None, 1, UserUpdateIn(email="a"))


@patch('right_the_ship.core.api.user.get_object_or_404')
def test_cannot_create_user_with_too_long_values(mock_get_object_or_404):
    mock_get_object_or_404.return_value = MagicMock(spec=User)

    with pytest.raises(ValidationError):
        update_user(None, 1, UserUpdateIn(username="a" * 51))

    with pytest.raises(ValidationError):
        update_user(None, 1, UserUpdateIn(password="a" * 51))

    with pytest.raises(ValidationError):
        update_user(None, 1, UserUpdateIn(email="a" * 51 + "@example.com"))
