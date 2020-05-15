import os
import requests
from django_rq import job

from core.models import TelegramBotLogs


@job
def send_telegram_audio(bot, message, url, title, duration):
    try:
        bot.send_chat_action(message.chat.id, action='upload_document')
        body = requests.get(url)

        filename = '/tmp/{}.mp3'.format(title.replace(' ', '+'))

        with open(filename, 'wb') as file:
            file.write(body.content)

        bot.send_audio(message.chat.id, audio=open(filename, 'rb'), title=title, duration=duration)

        delete_file.delay(filename)
    except Exception as e:
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e, log_type=1))


@job
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
