from django.db import models


class Log(models.Model):
    from_user = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    exception = models.TextField(blank=True, null=True)
    additional_text = models.TextField(blank=True, null=True)


class RQLog(models.Model):
    from_user = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_exception = models.BooleanField(default=False)
    exception_text = models.TextField(null=True, blank=True)


class TelegramBotLogs(models.Model):
    LOG_TYPE = (
        (0, 'Error'),
        (1, 'Not Sended'),
        (2, 'Not Found')
    )

    chat_id = models.IntegerField(blank=True)
    group = models.BooleanField(default=False)
    log_type = models.IntegerField(choices=LOG_TYPE, default=0)
    content = models.TextField(blank=True, null=True)
    exception = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_kwargs(message, e='', log_type=0):
        return {
            'chat_id': message.chat.id,
            'group': message.chat.type == 'group',
            'log_type': log_type,
            'content': message.chat.text,
            'exception': e,
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'language': message.json['from'].get('language_code')
        }
