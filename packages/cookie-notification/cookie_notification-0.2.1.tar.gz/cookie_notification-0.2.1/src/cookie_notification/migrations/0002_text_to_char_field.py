from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    dependencies = [
        ('cookie_notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookienotificationssetting',
            name='text',
            field=models.CharField(
                default=(
                    'Продолжая пользоваться сайтом, вы соглашаетесь на обработку файлов cookie с использованием '
                    'метрических программ. Это поможет сделать сайт более удобным и полезным для вас.'
                ),
                max_length=1000,
                verbose_name='Текст'
            ),
        ),
    ]
