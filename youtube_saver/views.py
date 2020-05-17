import re
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
from youtube_saver.utils import send_telegram_audio

bot = TeleBot(settings.TELEGRAM_BOT_YOUTUBE_TOKEN)


class YoutubeApiView(ModelViewSet):
    serializer_class = YoutubePostsSerializer
    queryset = YoutubePosts.objects.all()
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        url = self.request.GET.get('url')
        if not url or not re.findall(settings.YOUTUBE_REGEX, url)[-1]:
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
        urls = re.findall(settings.YOUTUBE_REGEX, message.text)
        if urls:
            with youtube_dl.YoutubeDL(settings.YOUTUBE_DOWNLOAD_PARAMS) as ydl:
                url_param = urls[0].find('&')
                result = ydl.extract_info(urls[0][:url_param] if url_param != -1 else urls[0], download=False)
                true_song = []

                for result_format in result['formats']:
                    if result_format['format_note'] == 'tiny':
                        true_song.append({
                            'format': result_format['format_id'],
                            'url': result_format['url']
                        })
                    if result_format['format_note'].startswith('DASH') and result_format['format_note'].find(
                            'audio') != -1:
                        true_song.append({
                            'format': result_format['format_id'],
                            'url': result_format['fragment_base_url']
                        })

                if true_song:
                    best_audio = sorted(true_song, key=lambda item: item['format'])[-1]['url']
                    send_telegram_audio(bot, message, best_audio, result['title'], result['duration'])
                else:
                    print('Not Found')
                    TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, log_type=2))
    except Exception as e:
        print(e)
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e))


def set_webhook(request=None):
    webhook_url = '{}://{}/{}/{}'.format(settings.PROTOCOL, settings.DOMAIN, 'api/youtube/webhook',
                                         settings.TELEGRAM_BOT_YOUTUBE_TOKEN)
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    if request:
        if request.GET.get('remove'):
            bot.remove_webhook()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_200_OK)


set_webhook()
