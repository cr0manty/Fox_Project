import re
import youtube_dl

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from telebot import TeleBot, types

from core.models import TelegramLogs
from youtube_saver.models import YoutubePosts, DownloadYoutubeMP3ShortLink
from youtube_saver.serializers import YoutubePostsSerializer, YoutubeFormatsSerializer
from youtube_saver.utils import get_download_url

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
        TelegramLogs.create_object(update.message if update.message else update.edited_message)
        bot.process_new_updates([update])
        return Response({'code': 200})


@bot.message_handler(commands=['active'])
def active_links(message):
    yesterday = timezone.now() - timezone.timedelta(days=1)
    links = DownloadYoutubeMP3ShortLink.objects.filter(username=message.from_user.username, created_at__gt=yesterday)
    msg = ''

    for link in links:
        time_left = str(link.created_at - yesterday).split('.')[0]
        msg += '{}\n{}\nExpires in: {}\n\n'.format(link.title, link.get_absolute_url(), time_left)

    if not msg:
        msg = 'No active links'
    bot.send_message(message.chat.id, msg)


@bot.message_handler()
def parse_message(message):
    text = get_download_url(message, func=bot.send_chat_action, chat_id=message.chat.id, action='typing')
    if text is not None:
        bot.send_message(message.chat.id, text)


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


if settings.TELEGRAM_BOT_ENABLE:
    set_webhook()
