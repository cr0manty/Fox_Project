from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.utils.timezone import now, timedelta
from django.db.models import Q

from .serializers import SongListSerializer
from songs.models import Song

from core.models import Log
from core.utils import get_vk_auth, get_vk_songs, IsFriend


class SearchSongsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = SongListSerializer

    def get_query(self):
        search = self.request.GET.get('search')
        query = Q()

        if search:
            query = Q(Q(artist__istartswith=search) | Q(
                name__istartswith=search))
        return query

    def get_queryset(self):
        return Song.objects.filter(self.get_query())


class FriendsSongsView(SearchSongsView):
    permission_classes = (IsAuthenticated, IsFriend)

    def get_query(self):
        user_id = self.kwargs.get('id')
        query = super().get_query()

        if user_id:
            query &= Q(users__id=user_id)

        return query


class UserSongListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = request.user
        song_id = int(request.GET.get('song_id', 0))

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
        except Exception as e:
            err_text = 'Cant connect to vk server'
            Log.objects.create(exception=str(e), additional_text=err_text, from_user=user.username)
            return Response(err_text, status=400)

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
