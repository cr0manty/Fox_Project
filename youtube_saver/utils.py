import uuid
import io
import os
import requests
from pydub import AudioSegment

from core.models import TelegramBotLogs


def send_telegram_audio(bot, message, url, title, duration):
    filename = '/tmp/{}.mp3'.format(uuid.uuid4())
    try:
        bot.send_chat_action(message.chat.id, action='typing')
        print('Downloading file')
        body = requests.get(url)

        print('Saving File')
        audio = AudioSegment.from_file(io.BytesIO(body.content))

        print('Converting File')
        audio = audio.export(filename, format='mp3', codec='mp3')

        print('Sending File')
        bot.send_chat_action(message.chat.id, action='upload_document')
        bot.send_audio(message.chat.id, audio=audio, title=title, duration=duration)

        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e, log_type=1))

