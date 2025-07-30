const cookieNotification__cookieName = 'userNotifiedAboutCookieUsage';

/**
 * {% comment %}Проставление разметки на сообщение
 * @param text
 * @param fileLink
 * @returns {*}{% endcomment %}
 */
function cookieNotification__buildMessageHTML(text, fileLink) {
    if (fileLink !== null) {
        return text.replace(/_([^_]+)_/g, '<a href="' + fileLink + '" target="_blank">$1</a>');
    } else {
        return text.replace(/_([^_]+)_/g, '$1');
    }
}

/**
 * {% comment %}Отображение окна оповещения.
 * @param text
 * @param fileLink
 * @returns {*}{% endcomment %}
 */
function cookieNotification__showNotification(text, fileLink) {
    var message = cookieNotification__buildMessageHTML(text, fileLink);

    Ext.Msg.show({
        title: "Внимание!",
        msg: message,
        closable: false,
        buttons: Ext.Msg.OK,
        fn: function(btn) {
            if (btn === 'ok') {
                Ext.Ajax.request({
                    url: '{{ cookie_notification.agreed_to_cookies_url }}',
                });
            }
        }
    });
}

function cookieNotification__bootstrap() {
    const alreadyNotified = Ext.util.Cookies.get(cookieNotification__cookieName);
    if (alreadyNotified) {
        return;
    }

    Ext.Ajax.request({
        url: '{{ cookie_notification.get_cookie_notification_settings_url }}',
        success: function (res, opts) {
            var jsonResponse = JSON.parse(res.responseText);
            cookieNotification__showNotification(jsonResponse.text, jsonResponse.file);
        }
    });
}

cookieNotification__bootstrap();
