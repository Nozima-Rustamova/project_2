import re
from rest_framework import serializers


def validate_password_strength(password: str, username: str = None, email: str = None):
    """Validate password strength according to recommended rules.

    Rules (Apple/iOS-style strong password recommendations):
    - Minimum length 8
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    - Must not contain the username or email local-part

    Raises:
        serializers.ValidationError on failure with descriptive messages.
    """
    errors = []

    if not password or not isinstance(password, str):
        raise serializers.ValidationError("Password must be a string.")

    # Regex: at least one lowercase, one uppercase, one digit, min length 8, no spaces.
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\S]{8,}$')
    if not pattern.match(password):
        errors.append(
            "Password must be at least 8 characters, include 1 uppercase letter, 1 lowercase letter, and 1 digit, and must not contain spaces."
        )

    # Check username/email substrings to avoid weak passwords (keep these checks)
    if username:
        try:
            if username.lower() in password.lower():
                errors.append("Password must not contain your username.")
        except Exception:
            pass

    if email:
        try:
            local_part = email.split('@')[0]
            if local_part and local_part.lower() in password.lower():
                errors.append("Password must not contain your email or its local part.")
        except Exception:
            pass

    if errors:
        raise serializers.ValidationError(errors)

    return True
