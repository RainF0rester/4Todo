import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from backend.modules.users.models import User
from backend.modules.users.service import AuthError, login_user


class TestLoginUser:
    """
    Tests for the login_user service function.

    This file focuses only on login-related business rules.
    """

    @patch("modules.users.service.get_user_by_username_or_email")
    @patch("modules.users.service.create_token")
    def test_login_user_success_with_username(self, mock_create_token, mock_get_user):
        """
        A user should be able to log in successfully using a username.
        """
        mock_session = MagicMock(spec=Session)

        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.check_password.return_value = True
        mock_user.to_json.return_value = {"id": 1, "username": "testuser", "email": "test@example.com"}
        mock_get_user.return_value = mock_user
        mock_create_token.return_value = "jwt_token_123"

        result = login_user(mock_session, "testuser", "password123")

        expected_result = {
            "user": {"id": 1, "username": "testuser", "email": "test@example.com"},
            "token": "jwt_token_123",
        }

        assert result == expected_result
        mock_get_user.assert_called_once_with(mock_session, "testuser")
        mock_user.check_password.assert_called_once_with("password123")
        mock_create_token.assert_called_once_with(
            user_id=1,
            username="testuser",
            email="test@example.com",
        )

    @patch("modules.users.service.get_user_by_username_or_email")
    @patch("modules.users.service.create_token")
    def test_login_user_success_with_email(self, mock_create_token, mock_get_user):
        """
        A user should be able to log in successfully using an email address.
        """
        mock_session = MagicMock(spec=Session)

        mock_user = MagicMock(spec=User)
        mock_user.id = 2
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.check_password.return_value = True
        mock_user.to_json.return_value = {"id": 2, "username": "testuser", "email": "test@example.com"}
        mock_get_user.return_value = mock_user
        mock_create_token.return_value = "jwt_token_456"

        result = login_user(mock_session, "test@example.com", "password123")

        expected_result = {
            "user": {"id": 2, "username": "testuser", "email": "test@example.com"},
            "token": "jwt_token_456",
        }

        assert result == expected_result
        mock_get_user.assert_called_once_with(mock_session, "test@example.com")
        mock_user.check_password.assert_called_once_with("password123")
        mock_create_token.assert_called_once_with(
            user_id=2,
            username="testuser",
            email="test@example.com",
        )

    @patch("modules.users.service.get_user_by_username_or_email")
    def test_login_user_invalid_identify(self, mock_get_user):
        """
        Login should fail when no matching user is found.
        """
        mock_session = MagicMock(spec=Session)
        mock_get_user.return_value = None

        with pytest.raises(AuthError, match="invalid identify"):
            login_user(mock_session, "nonexistent", "password123")

        mock_get_user.assert_called_once_with(mock_session, "nonexistent")

    @patch("modules.users.service.get_user_by_username_or_email")
    def test_login_user_invalid_password(self, mock_get_user):
        """
        Login should fail when the password is incorrect.
        """
        mock_session = MagicMock(spec=Session)

        mock_user = MagicMock(spec=User)
        mock_user.check_password.return_value = False
        mock_get_user.return_value = mock_user

        with pytest.raises(AuthError, match="invalid password"):
            login_user(mock_session, "testuser", "wrongpassword")

        mock_get_user.assert_called_once_with(mock_session, "testuser")
        mock_user.check_password.assert_called_once_with("wrongpassword")

    def test_login_user_empty_identify(self):
        """
        Login should fail when identify is empty.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="identify is required"):
            login_user(mock_session, "", "password123")

    def test_login_user_empty_password(self):
        """
        Login should fail when password is empty.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="password is required"):
            login_user(mock_session, "testuser", "")

    @patch("modules.users.service.get_user_by_username_or_email")
    @patch("modules.users.service.create_token")
    def test_login_user_input_stripping(self, mock_create_token, mock_get_user):
        """
        Identify and password should be stripped before authentication.
        """
        mock_session = MagicMock(spec=Session)

        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.check_password.return_value = True
        mock_user.to_json.return_value = {"id": 1, "username": "testuser", "email": "test@example.com"}
        mock_get_user.return_value = mock_user
        mock_create_token.return_value = "jwt_token_123"

        result = login_user(mock_session, "  testuser  ", "  password123  ")

        mock_get_user.assert_called_once_with(mock_session, "testuser")
        mock_user.check_password.assert_called_once_with("password123")
        assert result["token"] == "jwt_token_123"