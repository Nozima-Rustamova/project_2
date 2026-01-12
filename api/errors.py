from dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    code: str
    message: str


class ErrorCode:
    # ===== SUCCESS =====
    SUCCESS = Error(
        code="000",
        message="SUCCESS"
    )

    # ===== AUTH / LOGIN =====
    INVALID_CREDENTIALS = Error(
        code="ERROR_100",
        message="INVALID_CREDENTIALS"
    )

    USER_NOT_FOUND = Error(
        code="ERROR_101",
        message="USER_NOT_FOUND"
    )

    # ===== SIGNUP =====
    EMAIL_EXISTS = Error(
        code="ERROR_200",
        message="EMAIL_EXISTS"
    )

    WEAK_PASSWORD = Error(
        code="ERROR_201",
        message="WEAK_PASSWORD"
    )

    # ===== VALIDATION / GENERIC =====
    VALIDATION_FAILED = Error(
        code="ERROR_000",
        message="VALIDATION_FAILED"
    )

    GENERIC_ERROR = Error(
        code="ERROR_999",
        message="GENERIC_ERROR"
    )

    # ===== RESOURCE NOT FOUND =====
    POST_NOT_FOUND = Error(
        code="ERROR_301",
        message="POST_NOT_FOUND"
    )

    COMMENT_NOT_FOUND = Error(
        code="ERROR_302",
        message="COMMENT_NOT_FOUND"
    )

    PERMISSION_DENIED = Error(
        code="ERROR_403",
        message="PERMISSION_DENIED"
    )

    # ===== ACCOUNT =====
    ACCOUNT_DISABLED = Error(
        code="ERROR_410",
        message="ACCOUNT_DISABLED"
    )

    NOT_AUTHENTICATED = Error(
        code="ERROR_401",
        message="NOT_AUTHENTICATED"
    )

