import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from modules.users.models import User
from modules.users.service import ConflictError, register_user


class TestRegisterUser:
    """
    Tests for the register_user service function.

    This file focuses only on registration-related business rules.
    Some tests are marked as xfail because they are written in TDD style
    against the user story acceptance criteria, but the current service
    implementation does not support them yet.
    """

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    @patch("modules.users.service.create_user")
    def test_register_user_success(self, mock_create_user, mock_get_username, mock_get_email):
        """
        A new user with valid input should be registered successfully.
        """
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = None

        real_user = User(username="testuser", email="test@example.com", password_hash="")
        real_user.set_password("password123")
        real_user.id = 1
        mock_create_user.return_value = real_user

        result = register_user(mock_session, "testuser", "test@example.com", "password123")

        assert result == {"id": 1, "username": "testuser", "email": "test@example.com"}
        mock_get_email.assert_called_once_with(mock_session, "test@example.com")
        mock_get_username.assert_called_once_with(mock_session, "testuser")
        mock_create_user.assert_called_once()
        assert real_user.password_hash != ""

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    def test_register_user_email_conflict(self, mock_get_username, mock_get_email):
        """
        Registration should fail when the email has already been registered.
        """
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = MagicMock()

        with pytest.raises(ConflictError, match="email has already been registered"):
            register_user(mock_session, "testuser", "existing@example.com", "password123")

        mock_get_email.assert_called_once_with(mock_session, "existing@example.com")
        mock_get_username.assert_not_called()

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    def test_register_user_username_conflict(self, mock_get_username, mock_get_email):
        """
        Registration should fail when the username has already been registered.
        """
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = MagicMock()

        with pytest.raises(ConflictError, match="username has already been registered"):
            register_user(mock_session, "existinguser", "test@example.com", "password123")

        mock_get_email.assert_called_once_with(mock_session, "test@example.com")
        mock_get_username.assert_called_once_with(mock_session, "existinguser")

    def test_register_user_empty_username(self):
        """
        Registration should fail if username is empty.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="username is required"):
            register_user(mock_session, "", "test@example.com", "password123")

    def test_register_user_empty_email(self):
        """
        Registration should fail if email is empty.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="email is required"):
            register_user(mock_session, "testuser", "", "password123")

    def test_register_user_empty_password(self):
        """
        Registration should fail if password is empty.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="password is required"):
            register_user(mock_session, "testuser", "test@example.com", "")

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    @patch("modules.users.service.create_user")
    def test_register_user_email_normalization(self, mock_create_user, mock_get_username, mock_get_email):
        """
        Email should be stripped and converted to lowercase before validation and creation.
        """
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = None

        real_user = User(username="testuser", email="test@example.com", password_hash="")
        real_user.set_password("password123")
        real_user.id = 1
        mock_create_user.return_value = real_user

        register_user(mock_session, "testuser", "  TEST@EXAMPLE.COM  ", "password123")

        mock_get_email.assert_called_once_with(mock_session, "test@example.com")
        assert real_user.password_hash != ""

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    @patch("modules.users.service.create_user")
    def test_register_user_input_stripping(self, mock_create_user, mock_get_username, mock_get_email):
        """
        Username and password should be stripped before user creation.
        """
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = None

        real_user = User(username="testuser", email="test@example.com", password_hash="")
        real_user.set_password("password123")
        real_user.id = 1
        mock_create_user.return_value = real_user

        register_user(mock_session, "  testuser  ", "test@example.com", "  password123  ")

        mock_get_username.assert_called_once_with(mock_session, "testuser")
        assert real_user.password_hash != ""

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    @patch("modules.users.service.create_user")
    # @pytest.mark.xfail(reason="TDD: username max length validation (<= 16) not implemented yet")
    def test_register_user_rejects_username_longer_than_16(self, mock_create_user, mock_get_username, mock_get_email):
        """
        According to the user story, registration should reject usernames longer than 16 characters.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="username must be between 1 and 16 characters"):
            register_user(mock_session, "a" * 17, "test@unsw.edu.au", "password123")

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    @patch("modules.users.service.create_user")
    # @pytest.mark.xfail(reason="TDD: strict UNSW email domain validation not implemented yet")
    def test_register_user_rejects_invalid_email_format(self, mock_create_user, mock_get_username, mock_get_email):
        """
        Current service should reject invalid email format.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="email format is invalid"):
            register_user(mock_session, "testuser", "testgmail.com", "password123")

    @patch("modules.users.service.get_user_by_email")
    @patch("modules.users.service.get_user_by_username")
    @patch("modules.users.service.create_user")
    # @pytest.mark.xfail(reason="TDD: password max length validation (<= 30) not implemented yet")
    def test_register_user_rejects_password_longer_than_30(self, mock_create_user, mock_get_username, mock_get_email):
        """
        According to the user story, registration should reject passwords longer than 30 characters.
        """
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="password must be between 1 and 30 characters"):
            register_user(mock_session, "testuser", "test@unsw.edu.au", "a" * 31)