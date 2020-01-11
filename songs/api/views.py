from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.utils.timezone import now, timedelta
from django.db.models import Q


from .serializers import SongListSerializer
from songs.models import Song
from users.models import Relationship


from core.models import Log
from core.utils import get_vk_auth, get_vk_songs, get_vk_user_data


class UserSongListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = request.user
        user_id = request.GET.get('user_id', None)
        song_id = request.GET.get('song_id', None)

        if user_id:
            try:
                user = Relationship.objects.get(from_user=user, to_user__id=user_id)
            except Relationship.DoesNotExist:
                e = 'No relationships with this user'
                Log.objects.create(exception=e, from_user=user.username)
                return Response({'error': e}, status=403)

        query = Q(users=user)
        if song_id:
            query &= Q(song_id=song_id)

        songs = Song.objects.filter(query).all().order_by('song_id')
        serializer = SongListSerializer(songs, many=True)
        return Response({
            'user': user.id,
            'amount': len(songs),
            'songs': serializer.data
        })

    def post(self, request):
        user = request.user
        try:
            vk_session = get_vk_auth(user)
            audio_list = get_vk_songs(vk_session)
            user.set_vk_info(get_vk_user_data(vk_session)['id'])
        except Exception as e:
            err_text = 'Cant connect to vk server'
            Log.objects.create(exception=str(e), additional_text=err_text, from_user=user.username)
            return Response(err_text, status=500)

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
                    song.updated_at = now()
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
                Log.objects.create(exception=str(e), from_user=user.username)

        serializer = SongListSerializer(Song.objects.filter(posted_at__gte=now() - timedelta(minutes=5),
                                                            users=user).all().order_by('song_id'), many=True)
        songs_added.update({'songs': serializer.data})
        return Response(songs_added, status=201)
