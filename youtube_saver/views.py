import youtube_dl
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from youtube_saver.models import YoutubePosts
from youtube_saver.serializers import YoutubePostsSerializer


class YoutubeApiView(ModelViewSet):
    serializer_class = YoutubePostsSerializer
    queryset = YoutubePosts.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = 'slug'

    def create(self, request, *args, **kwargs):
        url = self.request.GET.get('url')
        if not url:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            with youtube_dl.YoutubeDL() as ydl:
                result = ydl.extract_info(url, download=False)
                serializer = self.get_serializer(data=result)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response('Something went wrong while trying to get data', status=status.HTTP_400_BAD_REQUEST)
