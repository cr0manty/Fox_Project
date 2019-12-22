from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from vk_api import VkApi, audio

from .serializers import SongListSerializer
from songs.models import Song
from users.models import UserLocation, Proxy, FriendList


def get_vk_audio(user):
    vk_session = VkApi(login=user.username, password=user.dump_password, config_filename='config.json')
    vk_session.auth()
    vk_session.get_api()
    return audio.VkAudio(vk_session)


class UserSongListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                return Response({'error': 'No relationships'}, status=403)

        songs = Song.objects.filter(users=user).all().order_by('-created_at')
        serializer = SongListSerializer(songs, many=True)
        return Response({request.user.user_id: {'songs': serializer.data}})

    def post(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                return Response({'error': 'No relationships with this user'}, status=403)

        user_location = UserLocation.objects.filter(user=user).order_by('-created_at').first()
        if user_location.need_proxy:
            return Response({'error': 'Proxy Authentication Required'}, status=407)

        audio_list = get_vk_audio(user).get(owner_id=user.user_id)
        songs_added = {
            'user': user.user_id,
            'amount': 0,
            'songs': [
            ]
        }

        for track in audio_list:
            try:
                try:
                    song = Song.objects.get(song_id=track.get('id'))
                    song.users.add(user)
                    song.save()
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
                    songs_added['songs'].append({
                        'artist': track.get('artist'),
                        'name': track.get('title'),
                        'duration': track.get('duration')
                    })
                    songs_added['amount'] += 1
            except:
                pass
        return Response(songs_added, status=201)
