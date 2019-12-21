from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from vk_api import VkApi, audio

from .serializers import SongListSerializer
from songs.models import Song
from users.models import UserLocation, Proxy


class UserSongListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if request.user.user_id != user_id:
            return Response(status=401)

        songs = Song.objects.filter(user__user_id=user_id).all().order_by('-created_at')
        serializer = SongListSerializer(songs, many=True)
        return Response({request.user.username: {'songs': serializer.data}})

    def post(self, request, user_id=None):
        user = request.user
        if user_id:
            return Response(status=401)

        user_location = UserLocation.objects.filter(user=user).order_by('-created_at').first()
        if user_location.need_proxy:
            return Response(status=407)

        vk_session = VkApi(login=user.username, password=user.dump_password, config_filename='config.json')
        vk_session.auth()
        vk_session.get_api()
        vk_audio = audio.VkAudio(vk_session)
        audio_list = vk_audio.get(owner_id=user.user_id)
        songs_added = {
            'user': user.user_id,
            'amount': 0,
            'songs': [
            ]
        }

        for track in audio_list:
            try:
                try:
                    song = Song.objects.filter(song_id=track.get('id')).first()
                except Song.DoesNotExist:
                    song = Song(
                        song_id=track.get('id'),
                        artist=track.get('artist'),
                        name=track.get('title'),
                        duration=track.get('duration'),
                        download=track.get('url'),
                    )
                song.users.add(user)
                song.save()

                songs_added['songs'].append({
                    'artist': track.get('artist'),
                    'name': track.get('title'),
                    'duration': track.get('duration')
                })
                songs_added['amount'] += 1
            except:
                pass
        return Response(songs_added, status=201)
