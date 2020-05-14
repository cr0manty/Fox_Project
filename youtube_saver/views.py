import re
import requests
import youtube_dl

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from telebot import TeleBot, types

from core.models import TelegramBotLogs
from youtube_saver.models import YoutubePosts
from youtube_saver.serializers import YoutubePostsSerializer, YoutubeFormatsSerializer

bot = TeleBot(settings.TELEGRAM_BOT_YOUTUBE_TOKEN)


class YoutubeApiView(ModelViewSet):
    serializer_class = YoutubePostsSerializer
    queryset = YoutubePosts.objects.all()
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        url = self.request.GET.get('url')
        if not url:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            with youtube_dl.YoutubeDL(settings.YOUTUBE_DOWNLOAD_PARAMS) as ydl:
                result = ydl.extract_info(url, download=False)
                formats = result.pop('formats')
                serializer = self.get_serializer(data=result)
            if serializer.is_valid():
                serializer.save()
                data = serializer.data

                formats_serializer = YoutubeFormatsSerializer(data=formats, many=True)
                if formats_serializer.is_valid():
                    data.update({'formats': formats_serializer.data})

                return Response(data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response('Something went wrong while trying to get data', status=status.HTTP_400_BAD_REQUEST)


class TelegramBotView(APIView):
    def post(self, request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return Response({'code': 200})


@bot.message_handler()
def parse_message(message):
    try:
        urls = re.findall(
            r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?',
            message.text)
        if urls:
            with youtube_dl.YoutubeDL(settings.YOUTUBE_DOWNLOAD_PARAMS) as ydl:
                url_param = urls[0].find('&')
                result = ydl.extract_info(urls[0][:url_param] if url_param != -1 else urls[0], download=False)
                true_song = []

                for result_format in result['formats']:
                    if result_format['format_note'] == 'tiny' or result_format['format_note'].startswith('DASH'):
                        true_song.append(result_format)

                if true_song:
                    try:
                        bot.send_chat_action(message.chat.id, action='upload_audio')
                        body = requests.get(sorted(true_song, key=lambda item: item['format_id'])[-1]['url'])
                        bot.send_audio(message.chat.id, audio=body.content, title=result['title'])
                    except Exception as e:
                        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e, log_type=1))
                else:
                    TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, log_type=2))
    except Exception as e:
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e))


webhook_url = '{}://{}/{}/{}'.format(settings.PROTOCOL, settings.DOMAIN, 'api/youtube/webhook',
                                     settings.TELEGRAM_BOT_YOUTUBE_TOKEN)
bot.set_webhook(url=webhook_url)
