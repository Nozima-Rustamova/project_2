from .local import en, ru, uz

LANGUAGES = {
    "en": en.MESSAGES,
    "ru": ru.MESSAGES,
    "uz": uz.MESSAGES,
}

DEFAULT_LANG = "en"


def get_language(request):
    header = request.headers.get("Accept-Language", "")
    lang = header.split(",")[0].lower()
    return lang if lang in LANGUAGES else DEFAULT_LANG


def translate(code: str, lang: str) -> str:
    return LANGUAGES.get(lang, {}).get(code, code)
