from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from api.errors import ErrorCode  

def custom_exception_handler(exc, context):
    if isinstance(exc, NotAuthenticated):
        return Response(
            {
                "error_code": ErrorCode.NOT_AUTHENTICATED.code,
                "data": {
                    "message": ErrorCode.NOT_AUTHENTICATED.message
                }
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "error_code": ErrorCode.PERMISSION_DENIED.code,
                "data": {
                    "message": ErrorCode.PERMISSION_DENIED.message
                }
            },
            status=status.HTTP_403_FORBIDDEN
        )

    return exception_handler(exc, context)
