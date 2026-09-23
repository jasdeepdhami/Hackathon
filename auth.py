import bcrypt
from database import (
    create_user,
    get_user_by_username)
def login_user(username, password):
    user = get_user_by_username(username)

    if user is None:
        return None

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if password_correct:
        return user

    return None
def signup_user(
    username,
    password,
    first_name,
    last_name,
    phone_number,
    email,
):
    # Check if username already exists
    existing_user = get_user_by_username(username)

    if existing_user is not None:
        return False, "Username already exists."

    # Basic validation
    if not username.strip():
        return False, "Username is required."

    if not password:
        return False, "Password is required."

    if not first_name.strip():
        return False, "First name is required."

    if not last_name.strip():
        return False, "Last name is required."

    if not email.strip():
        return False, "Email is required."

    # Create user
    user_id = create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email
    )

    if user_id is not None:
        return True, user_id

    return False, "Unable to create account."
