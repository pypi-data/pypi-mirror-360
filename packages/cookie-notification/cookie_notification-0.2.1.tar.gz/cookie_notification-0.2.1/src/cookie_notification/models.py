from django.conf import (
    settings,
)
from django.core.validators import (
    FileExtensionValidator,
)
from django.db import (
    models,
)

from cookie_notification.domain import (
    DEFAULT_NOTIFICATION_TEXT,
)

from educommon.audit_log.models import (
    LoggableModelMixin,
)
from educommon.django.db.validators.simple import (
    FileMimeTypeValidator,
)


class CookieNotificationsSetting(LoggableModelMixin, models.Model):
    """Настройки уведомлений об использовании файлов cookie."""

    text = models.CharField(
        verbose_name='Текст',
        default=DEFAULT_NOTIFICATION_TEXT,
        max_length=1000,
    )
    file = models.FileField(
        verbose_name='Файл',
        upload_to=settings.COOKIE_LIC_AGREEMENT_FILE_DIR,
        null=True, blank=True,
        validators=(
            FileExtensionValidator(allowed_extensions=settings.EXTENSIONS),
            FileMimeTypeValidator(allowed_extensions=settings.EXTENSIONS),
        ),
    )

    class Meta:
        db_table = 'cookie_notifications_setting'
        verbose_name = 'Настройки уведомлений об использовании файлов cookie'
        verbose_name_plural = 'Настройки уведомлений об использовании файлов cookie'
