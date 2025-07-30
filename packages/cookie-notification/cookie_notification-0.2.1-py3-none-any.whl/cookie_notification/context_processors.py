from pathlib import (
    Path,
)
from typing import (
    Union,
)

from django.conf import (
    settings,
)
from django.utils.module_loading import (
    import_string,
)


def cookie_notification(request) -> dict[str, Union[dict, str]]:
    """Возвращает необходимый контекст для шаблона в РИС."""

    pack = import_string(settings.COOKIE_NOTIFICATION_PACK_PATH)

    return {
        'cookie_notification': {
            'enabled': settings.DO_COOKIE_NOTIFICATION,
            'agreed_to_cookies_url': pack.set_cookie_notification_agreement_action.get_absolute_url(),
            'get_cookie_notification_settings_url': pack.cookie_notification_message_action.get_absolute_url(),
        },
        'cookie_notification_template_path': str(
            Path(Path(__file__).parent / 'web/templates/ui-js/cookie-notification.js').absolute()
        ),
    }
