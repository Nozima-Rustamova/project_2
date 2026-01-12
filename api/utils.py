from rest_framework.response import Response
from rest_framework import status
from .errors import ErrorCode
from .localization import get_language, translate


def api_response(
    error,
    request=None,
    message=None,
    data=None,
    status_code=status.HTTP_200_OK,
):
    if data is None:
        data = {}

    if hasattr(error, "code"):
        code = error.code
    else:
        code = str(error)

    lang = get_language(request) if request else "en"

    final_message = (
        message
        if message is not None
        else translate(code, lang)
    )

    payload = {
        "error_code": code,
        "message": final_message,
        "data": data,
    }

    return Response(payload, status=status_code)

