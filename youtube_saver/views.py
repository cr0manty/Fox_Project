import youtube_dl
from django.conf import settings
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
