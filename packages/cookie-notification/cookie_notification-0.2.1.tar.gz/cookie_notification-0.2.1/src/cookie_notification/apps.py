from django.apps.config import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):
    name = __package__
