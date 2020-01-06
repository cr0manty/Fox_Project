from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.utils.timezone import now, timedelta

from vk_api import VkApi, audio
# from datetime import datetime, timedelta

from .serializers import SongListSerializer
from songs.models import Song
from users.models import UserLocation, Proxy, FriendList
from requests.exceptions import ConnectionError


def get_vk_audio(user):
    try:
        login = user.vk_login if user.vk_login else user.username
        vk_session = VkApi(login=login, password=user.vk_password, config_filename='config.json')
        vk_session.auth()
        vk_session.get_api()
        return audio.VkAudio(vk_session)
    except ConnectionError as e:
        print(e)


# test id 356189219
class UserSongListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                return Response({'error': 'No relationships'}, status=403)

        songs = Song.objects.filter(users=user).all().order_by('song_id')
        serializer = SongListSerializer(songs, many=True)
        return Response({
            'user': user.id,
            'amount': len(songs),
            'songs': serializer.data
        })

    def post(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                return Response({'error': 'No relationships with this user'}, status=403)

        # user_location = UserLocation.objects.filter(user=user).order_by('-created_at').first()
        # if user_location.need_proxy:
        #     return Response({'error': 'Proxy Authentication Required'}, status=407)

        audio_list = get_vk_audio(user).get(owner_id=user.user_id)
        songs_added = {
            'user': user.id,
            'added': 0,
            'updated': 0,
            'songs': [
            ]
        }

        for track in audio_list:
            try:
                try:
                    song = Song.objects.get(song_id=track.get('id'))
                    song.users.add(user)
                    song.download = track['url']
                    song.save()
                    songs_added['updated'] += 1
                except Song.DoesNotExist:
                    song = Song.objects.create(
                        song_id=track.get('id'),
                        artist=track.get('artist'),
                        name=track.get('title'),
                        duration=track.get('duration'),
                        download=track.get('url'),
                    )
                    song.users.add(user)
                    song.save()
                    songs_added['added'] += 1
            except Exception as e:
                print(e)

        serializer = SongListSerializer(Song.objects.filter(posted_at__gte=now() - timedelta(minutes=7),
                                                            users=user).all().order_by('song_id'), many=True)
        songs_added.update({'songs': serializer.data})
        return Response(songs_added, status=201)
