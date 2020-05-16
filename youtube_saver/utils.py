import uuid
import io
import os
import requests

from datetime import datetime, timedelta

from django.conf import settings
from django_rq import get_scheduler
from pydub import AudioSegment

from core.models import TelegramBotLogs


def send_telegram_audio(bot, message, url, title, duration):
    filename = os.path.join(settings.MEDIA_ROOT, '{}.mp3'.format(uuid.uuid4()))

    try:
        bot.send_chat_action(message.chat.id, action='typing')
        print('Downloading file')
        body = requests.get(url)
        if body.status_code == 200:
            print('Saving File')
            audio = AudioSegment.from_file(io.BytesIO(body.content))

            print('Converting File')
            audio = audio.export(filename, format='mp3', codec='mp3')

            print('Sending File')
            bot.send_chat_action(message.chat.id, action='upload_document')
            bot.send_audio(message.chat.id, audio=audio, title=title, duration=duration)
            start_delete(filename)
        else:
            print('Not Found')
            start_delete(filename)
            TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=url, log_type=2))
    except Exception as e:
        print(e)
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e, log_type=1))


def start_delete(filename):
    scheduler = get_scheduler('default')
    scheduler.enqueue_at(datetime.now() + timedelta(minutes=20), delete_file, filename=filename)


def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
