from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CookieNotificationsSetting',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('text',
                 models.TextField(
                     default=(
                         'Продолжая пользоваться сайтом, вы соглашаетесь на обработку файлов cookie с '
                         'использованием метрических программ. Это поможет сделать сайт более удобным и '
                         'полезным для вас.'
                     ),
                     verbose_name='Текст')),
                ('file',
                 models.FileField(
                    # upload_to указывается в настройках, тут нарочно оставлено пустое значение
                     upload_to='',
                     verbose_name='Файл',
                     null=True, blank=True,
                 )),
            ],
            options={
                'verbose_name':
                    'Настройки уведомлений об использовании файлов cookie',
                'verbose_name_plural':
                    'Настройки уведомлений об использовании файлов cookie',
                'db_table': 'cookie_notifications_setting',
            },
        ),
    ]
