import pytest
from pydantic import ValidationError
from app.schemas.base import UserBase, PasswordMixin, UserCreate, UserLogin


def test_user_base_valid():
    """Test UserBase with valid data."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
    }
    user = UserBase(**data)
    assert user.first_name == "John"
    assert user.email == "john.doe@example.com"


def test_user_base_invalid_email():
    """Test UserBase with invalid email."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "invalid-email",
        "username": "johndoe",
    }
    with pytest.raises(ValidationError):
        UserBase(**data)


def test_password_mixin_valid():
    """Test PasswordMixin with valid password."""
    data = {"password": "SecurePass123"}
    password_mixin = PasswordMixin(**data)
    assert password_mixin.password == "SecurePass123"


def test_password_mixin_invalid_short_password():
    """Test PasswordMixin with short password."""
    data = {"password": "short"}
    with pytest.raises(ValidationError):
        PasswordMixin(**data)


def test_password_mixin_no_uppercase():
    """Test PasswordMixin with no uppercase letter."""
    data = {"password": "lowercase1"}
    with pytest.raises(ValidationError, match="Password must contain at least one uppercase letter"):
        PasswordMixin(**data)


def test_password_mixin_no_lowercase():
    """Test PasswordMixin with no lowercase letter."""
    data = {"password": "UPPERCASE1"}
    with pytest.raises(ValidationError, match="Password must contain at least one lowercase letter"):
        PasswordMixin(**data)


def test_password_mixin_no_digit():
    """Test PasswordMixin with no digit."""
    data = {"password": "NoDigitsHere"}
    with pytest.raises(ValidationError, match="Password must contain at least one digit"):
        PasswordMixin(**data)


def test_user_create_valid():
    """Test UserCreate with valid data."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "SecurePass123",
    }
    user_create = UserCreate(**data)
    assert user_create.username == "johndoe"
    assert user_create.password == "SecurePass123"


def test_user_create_invalid_password():
    """Test UserCreate with invalid password."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "short",
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_user_login_valid():
    """Test UserLogin with valid data."""
    data = {"username": "johndoe", "password": "SecurePass123"}
    user_login = UserLogin(**data)
    assert user_login.username == "johndoe"


def test_user_login_invalid_username():
    """Test UserLogin with short username."""
    data = {"username": "jd", "password": "SecurePass123"}
    with pytest.raises(ValidationError):
        UserLogin(**data)


def test_user_login_invalid_password():
    """Test UserLogin with invalid password."""
    data = {"username": "johndoe", "password": "short"}
    with pytest.raises(ValidationError):
        UserLogin(**data)


def test_password_strength_valid():
    # A password that meets all criteria should pass
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="StrongPass1!",
        confirm_password="StrongPass1!"
    )
    assert user.password == "StrongPass1!"

@pytest.mark.parametrize("password,error_message", [
    ("short1!", "String should have at least 8 characters"),
    ("alllowercase1!", "Password must contain at least one uppercase letter"),
    ("ALLUPPERCASE1!", "Password must contain at least one lowercase letter"),
    ("NoDigits!", "Password must contain at least one digit"),
    ("NoSpecialChars1", "Password must contain at least one special character"), need to get this working!
])
def test_password_strength_invalid(password, error_message):

    with pytest.raises(ValueError) as exc_info:
        UserCreate(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password=password,
            confirm_password=password
        )
    print(f"password {password} is throwing error {str(exc_info.value)}")
    assert error_message in str(exc_info.value)