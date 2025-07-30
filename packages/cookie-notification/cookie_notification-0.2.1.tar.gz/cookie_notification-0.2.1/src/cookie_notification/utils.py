from typing import (
    Optional,
)


_AGREEMENT_TO_COOKIES_REQUEST_ATTR = '_do_set_cookie_notification_agreement'


def get_agreement_from_request(request) -> Optional[bool]:
    """
    Получение признака, был ли запрос согласием на использование cookie.
    """

    return getattr(request, _AGREEMENT_TO_COOKIES_REQUEST_ATTR, None)


def set_agreement_to_request(request):
    """
    Проставление признака, был ли запрос согласием на использование cookie.
    """

    setattr(request, _AGREEMENT_TO_COOKIES_REQUEST_ATTR, True)
