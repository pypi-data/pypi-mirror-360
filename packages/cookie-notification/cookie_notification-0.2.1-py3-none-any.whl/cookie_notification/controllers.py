from datetime import (
    datetime,
)

from objectpack import (
    observer,
)

from cookie_notification.const import (
    CONFIRMATION_COOKIE_EXPIRES_AT,
)
from cookie_notification.utils import (
    get_agreement_from_request,
)


class CookieController(observer.ObservableController):
    """
    Контроллер, отвечающий за работу "публичной" части
    уведомлений и проставление куки, отмечающей согласие.
    """

    def process_request(self, request):
        response = super().process_request(request)

        if get_agreement_from_request(request):
            response.set_cookie(
                'userNotifiedAboutCookieUsage', 't', httponly=False, expires=CONFIRMATION_COOKIE_EXPIRES_AT,
            )

        return response
