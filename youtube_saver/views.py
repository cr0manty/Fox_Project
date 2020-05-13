import json

import requests
import youtube_dl

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from youtube_saver.models import YoutubePosts
from youtube_saver.serializers import YoutubePostsSerializer, YoutubeFormatsSerializer


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


class TelegramBotView(View):
    def post(self, request, *args, **kwargs):
        t_data = json.loads(request.body)

        t_message = t_data["message"]
        t_chat = t_message["chat"]

        return JsonResponse({"ok": "POST request processed"})

    # def parse_message(message):
    #     try:
    #         urls = re.findall(r'(?P<url>https?://[^\s]+)', message.text)
    #         if urls:
    #             with youtube_dl.YoutubeDL({
    #                 'format': 'bestaudio/best',
    #                 'postprocessors': [{
    #                     'key': 'FFmpegExtractAudio',
    #                     'preferredcodec': 'mp3',
    #                     'preferredquality': '320',
    #                 }],
    #             }) as ydl:
    #                 url_param = urls[0].find('&')
    #                 result = ydl.extract_info(urls[0][:url_param] if url_param != -1 else urls[0], download=False)
    #                 bot.send_chat_action(message.chat.id, action='sending')
    #                 true_song = []
    #
    #                 for result_format in result['formats']:
    #                     if result_format['format_note'] == 'tiny':
    #                         true_song.append(result_format)
    #                     else:
    #                         break
    #                 if true_song:
    #                     body = requests.get(sorted(true_song, key=lambda item: item['format_id'])[-1]['url'])
    #                     bot.send_audio(message.chat.id, audio=body.content, title=result['title'])
    #     except Exception as e:
    #         print(e)

    @staticmethod
    def data(chat_id, parse_mode, additional=None):
        data = {"chat_id": chat_id}
        if parse_mode:
            data['parse_mode'] = parse_mode

        if additional:
            data.update(additional)

        return data

    @staticmethod
    def send(action, data=None):
        if data is not dict:
            data = {}
        requests.post(
            f"{settings.TELEGRAM_URL}{settings.TELEGRAM_BOT_YOUTUBE_TOKEN}/{action}", data=data
        )
