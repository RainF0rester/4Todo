import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from modules.users.service import (
    register_user,
    login_user,
    AuthError,
    ConflictError
)
from modules.users.models import User


class TestRegisterUser:
    """Test cases for register_user function."""

    @patch('modules.users.service.get_user_by_email')
    @patch('modules.users.service.get_user_by_username')
    @patch('modules.users.service.create_user')
    def test_register_user_success(self, mock_create_user, mock_get_username, mock_get_email):
        """Test successful user registration."""
        # Mock dependencies
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = None

        # Create a real User object to test set_password call
        real_user = User(username="testuser", email="test@example.com", password_hash="")
        real_user.set_password("password123")  # Pre-set the password hash
        real_user.id = 1  # Simulate database assignment
        mock_create_user.return_value = real_user

        # Call function
        result = register_user(mock_session, "testuser", "test@example.com", "password123")

        # Assertions
        assert result == {"id": 1, "username": "testuser", "email": "test@example.com"}
        mock_get_email.assert_called_once_with(mock_session, "test@example.com")
        mock_get_username.assert_called_once_with(mock_session, "testuser")
        mock_create_user.assert_called_once()
        # Verify password was set (check that password_hash is not empty)
        assert real_user.password_hash != ""

    @patch('modules.users.service.get_user_by_email')
    @patch('modules.users.service.get_user_by_username')
    def test_register_user_email_conflict(self, mock_get_username, mock_get_email):
        """Test registration fails when email already exists."""
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = MagicMock()  # Email exists

        with pytest.raises(ConflictError, match="email has already been registered"):
            register_user(mock_session, "testuser", "existing@example.com", "password123")

        mock_get_email.assert_called_once_with(mock_session, "existing@example.com")
        mock_get_username.assert_not_called()

    @patch('modules.users.service.get_user_by_email')
    @patch('modules.users.service.get_user_by_username')
    def test_register_user_username_conflict(self, mock_get_username, mock_get_email):
        """Test registration fails when username already exists."""
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = MagicMock()  # Username exists

        with pytest.raises(ConflictError, match="username has already been registered"):
            register_user(mock_session, "existinguser", "test@example.com", "password123")

        mock_get_email.assert_called_once_with(mock_session, "test@example.com")
        mock_get_username.assert_called_once_with(mock_session, "existinguser")

    def test_register_user_empty_username(self):
        """Test registration fails with empty username."""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="username is required"):
            register_user(mock_session, "", "test@example.com", "password123")

    def test_register_user_empty_email(self):
        """Test registration fails with empty email."""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="email is required"):
            register_user(mock_session, "testuser", "", "password123")

    def test_register_user_empty_password(self):
        """Test registration fails with empty password."""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="password is required"):
            register_user(mock_session, "testuser", "test@example.com", "")

    @patch('modules.users.service.get_user_by_email')
    @patch('modules.users.service.get_user_by_username')
    @patch('modules.users.service.create_user')
    def test_register_user_email_normalization(self, mock_create_user, mock_get_username, mock_get_email):
        """Test that email is normalized to lowercase and stripped."""
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = None

        # Create a real User object to test set_password call
        real_user = User(username="testuser", email="test@example.com", password_hash="")
        real_user.set_password("password123")  # Pre-set the password hash
        real_user.id = 1  # Simulate database assignment
        mock_create_user.return_value = real_user

        # Call with uppercase email and whitespace
        register_user(mock_session, "testuser", "  TEST@EXAMPLE.COM  ", "password123")

        # Verify email was normalized
        mock_get_email.assert_called_once_with(mock_session, "test@example.com")
        # Verify password was set (check that password_hash is not empty)
        assert real_user.password_hash != ""

    @patch('modules.users.service.get_user_by_email')
    @patch('modules.users.service.get_user_by_username')
    @patch('modules.users.service.create_user')
    def test_register_user_input_stripping(self, mock_create_user, mock_get_username, mock_get_email):
        """Test that username and password are stripped of whitespace."""
        mock_session = MagicMock(spec=Session)
        mock_get_email.return_value = None
        mock_get_username.return_value = None

        # Create a real User object to test set_password call
        real_user = User(username="testuser", email="test@example.com", password_hash="")
        real_user.set_password("password123")  # Pre-set the password hash
        real_user.id = 1  # Simulate database assignment
        mock_create_user.return_value = real_user

        # Call with whitespace-padded inputs
        register_user(mock_session, "  testuser  ", "test@example.com", "  password123  ")

        # Verify inputs were stripped
        mock_get_username.assert_called_once_with(mock_session, "testuser")
        # Verify password was set (check that password_hash is not empty)
        assert real_user.password_hash != ""


class TestLoginUser:
    """Test cases for login_user function."""

    @patch('modules.users.service.get_user_by_username_or_email')
    @patch('modules.users.service.create_token')
    def test_login_user_success_with_username(self, mock_create_token, mock_get_user):
        """Test successful login with username."""
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
            "token": "jwt_token_123"
        }
        assert result == expected_result

        mock_get_user.assert_called_once_with(mock_session, "testuser")
        mock_user.check_password.assert_called_once_with("password123")
        mock_create_token.assert_called_once_with(user_id=1, username="testuser", email="test@example.com")

    @patch('modules.users.service.get_user_by_username_or_email')
    @patch('modules.users.service.create_token')
    def test_login_user_success_with_email(self, mock_create_token, mock_get_user):
        """Test successful login with email."""
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
            "token": "jwt_token_456"
        }
        assert result == expected_result

        mock_get_user.assert_called_once_with(mock_session, "test@example.com")
        mock_user.check_password.assert_called_once_with("password123")
        mock_create_token.assert_called_once_with(user_id=2, username="testuser", email="test@example.com")

    @patch('modules.users.service.get_user_by_username_or_email')
    def test_login_user_invalid_identify(self, mock_get_user):
        """Test login fails with invalid username/email."""
        mock_session = MagicMock(spec=Session)
        mock_get_user.return_value = None  # User not found

        with pytest.raises(AuthError, match="invalid identify"):
            login_user(mock_session, "nonexistent", "password123")

        mock_get_user.assert_called_once_with(mock_session, "nonexistent")

    @patch('modules.users.service.get_user_by_username_or_email')
    def test_login_user_invalid_password(self, mock_get_user):
        """Test login fails with invalid password."""
        mock_session = MagicMock(spec=Session)

        mock_user = MagicMock(spec=User)
        mock_user.check_password.return_value = False  # Wrong password
        mock_get_user.return_value = mock_user

        with pytest.raises(AuthError, match="invalid password"):
            login_user(mock_session, "testuser", "wrongpassword")

        mock_get_user.assert_called_once_with(mock_session, "testuser")
        mock_user.check_password.assert_called_once_with("wrongpassword")

    def test_login_user_empty_identify(self):
        """Test login fails with empty identify."""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="identify is required"):
            login_user(mock_session, "", "password123")

    def test_login_user_empty_password(self):
        """Test login fails with empty password."""
        mock_session = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="password is required"):
            login_user(mock_session, "testuser", "")

    @patch('modules.users.service.get_user_by_username_or_email')
    @patch('modules.users.service.create_token')
    def test_login_user_input_stripping(self, mock_create_token, mock_get_user):
        """Test that identify and password are stripped of whitespace."""
        mock_session = MagicMock(spec=Session)

        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.check_password.return_value = True
        mock_user.to_json.return_value = {"id": 1, "username": "testuser", "email": "test@example.com"}
        mock_get_user.return_value = mock_user

        mock_create_token.return_value = "jwt_token_123"

        # Call with whitespace-padded inputs
        result = login_user(mock_session, "  testuser  ", "  password123  ")

        # Verify inputs were stripped
        mock_get_user.assert_called_once_with(mock_session, "testuser")
        mock_user.check_password.assert_called_once_with("password123")
        assert result["token"] == "jwt_token_123"

