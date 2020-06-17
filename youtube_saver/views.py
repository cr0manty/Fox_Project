import re
import uuid

import youtube_dl

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from telebot import TeleBot, types

from core.models import TelegramBotLogs
from youtube_saver.models import YoutubePosts, DownloadYoutubeMP3ShortLink
from youtube_saver.serializers import YoutubePostsSerializer, YoutubeFormatsSerializer

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
    try:
        urls = re.findall(settings.YOUTUBE_REGEX, message.text)
        if urls:
            with youtube_dl.YoutubeDL(settings.YOUTUBE_DOWNLOAD_PARAMS) as ydl:
                url_param = urls[0].find('&')
                result = ydl.extract_info(urls[0][:url_param] if url_param != -1 else urls[0], download=False)
                bot.send_chat_action(message.chat.id, action='typing')
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
                    url = create_short_url(result, best_audio, message.from_user.username)
                    bot.send_message(message.chat.id,
                                     '{} \n\nThis link is open just for 24 hours'.format(url.get_absolute_url()))
                else:
                    print('Not Found')
                    TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, log_type=2))
    except Exception as e:
        print(e)
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e))


def create_short_url(result, song_url, username, slug_length=8):
    slug = str(uuid.uuid4())[:slug_length]
    try:
        link = DownloadYoutubeMP3ShortLink.objects.get(slug=slug)
        yesterday = timezone.now() - timezone.timedelta(days=1)
        if link.created_at <= yesterday:
            link.delete()
        return create_short_url(result, song_url, username, slug_length + 2)
    except DownloadYoutubeMP3ShortLink.DoesNotExist:
        return DownloadYoutubeMP3ShortLink.objects.create(url=song_url, title=result.get('title'),
                                                          original_url=song_url, slug=slug, username=username,
                                                          duration=result.get('duration'))


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
