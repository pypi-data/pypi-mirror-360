# Уведомление пользователя об использовании cookie-файлов

## Установка

1. Создать приложение-адаптер на стороне РИС. В РИС должен регистрироваться:
- Конкретный пак, унаследовавший логику `CookieNotificationsSettingsPack` - в нем происходит работа
с настройками;
- Конкретный пак, унаследовавший логику `CookieNotificationPublicPack`. Для п.2 требуется, чтобы
до экземпляра пака был конкретный путь. В зависимости от настроек прав пак может быть зарегистрирован в
контроллере, на котором не производится проверка авторизации. Этот пак нужно регистрировать в контроллере
`cookie_notification.controllers.CookieController` или его наследнике;
- Для классического дизайна с ExtJS - зарегистрировать context processor для добавления в шаблон страницы параметров 
```python
from ssuz.desktop.model import (
    Desktop,
)

Desktop.install_context_processor('cookie_notification.context_processors.cookie_notification')
```

Для паков следует настроить соответствующие права, если нужно. По умолчанию `CookieNotificationsSettingsPack`
доступен только для администраторов.

2. Добавить в проект настройки:

- `DO_COOKIE_NOTIFICATION` - `True`/`False` (по умолчанию `True`) - включает уведомление;
- `COOKIE_LIC_AGREEMENT_FILE_DIR` - директория, в которой будет храниться загруженный пользователем файл;
- `COOKIE_NOTIFICATION_PACK_PATH` - путь до пака, в котором находятся экшены 
`cookie_notification_message_action` и `set_cookie_notification_agreement_action`.
`cookie_notification_message_action` возвращает JSON с сообщением и адресом файла, а `set_cookie_notification_agreement_action` -
- экшен, на который будет реагировать контроллер `CookieController` при проставлении cookie, из которой будет следовать, что согласие было получено.
3. Добавить скрипт для отображения оповещения в шаблон страницы.
```html
{% if cookie_notification.enabled %}
    {% include cookie_notification_template_path %}
{% endif %}
```
Может потребоваться провести отдельную работу для прокидывания в контекст шаблона параметров из
`cookie_notification.context_processors.cookie_notification`.

## Примечания для фронтэнд-приложения не на ExtJS

Установка для приложений не на ExtJS будет включать первый пункт, где регистрируется пак, второй, где
добавляются настройки, и третий, где добавляется middleware. Добавление context processor нужно для
прокидывания параметров в шаблон. Как это будет реализовано в конкретном фронтэнде - это задача, которую нужно
будет решить. Сам скрипт отображения окна согласия также должен быть реализован на стороне конкретного фронтэнда.

При реализации отображения окна оповещения можно использовать как эндпойнты экшены
`cookie_notification_message_action` и `set_cookie_notification_agreement_action`.
