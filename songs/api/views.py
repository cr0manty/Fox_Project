from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.utils.timezone import now, timedelta
from django.db.models import Q

from core.views import AmountModelViewSet
from .serializers import SongListSerializer
from songs.models import Song

from api.models import IsFriend
from core.models import Log
from core.utils import get_vk_auth, get_vk_songs


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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsFriend)

    def get_query(self):
        user_id = self.kwargs.get('id')
        query = super().get_query()

        if user_id:
            query &= Q(users__id=user_id)

        return query


class RemoveSongFromUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, song_id):
        try:
            song = Song.objects.get(song_id=song_id, users=request.user)
            song.ignore_user(request.user)
            return Response(status=201)
        except Song.DoesNotExist:
            return Response(status=404)


class UserSongListAPIView(AmountModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Song.objects.all().order_by('song_id')
    serializer_class = SongListSerializer

    def get_filter_query(self):
        song_id = self.request.GET.get('song_id', None)
        query = Q(users=self.request.user)

        if song_id is not None:
            return query & Q(song_id=song_id)

        return query

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            vk_session = get_vk_auth(user)
            audio_list = get_vk_songs(vk_session)
        except Exception as e:
            err_text = 'Cant connect to vk server'
            Log.objects.create(exception=str(e), additional_text=err_text, from_user=user.username)
            return Response(err_text, status=400)

        songs_added = {
            'added': 0,
            'updated': 0,
        }

        for track in audio_list:
            try:
                try:
                    song = Song.objects.get(song_id=track.get('id'))
                    if user not in song.users_ignore.all():
                        song.users.add(user)
                        songs_added['updated'] += 1
                    song.download = track['url']
                    song.updated_at = now()
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
                    songs_added['added'] += 1
            except Exception as e:
                Log.objects.create(exception=str(e), from_user=user.username)

        return Response(songs_added, status=201)
