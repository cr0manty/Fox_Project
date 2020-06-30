import datetime
import re
import json

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.utils.timezone import now
from django.db.models import Q
from vk_audio import audio, Audio_obj

from api.serializers import StandardResultsSetPagination
from core.views import AmountModelViewSet
from .serializers import SongListSerializer
from songs.models import Song

from api.models import IsFriend
from core.models import Log, VKAuthMixin


class SearchSongsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = SongListSerializer

    def get_query(self):
        search = self.request.GET.get('search', '')

        if search:
            yesterday = timezone.now() - timezone.timedelta(days=1)
            return Q(Q(artist__istartswith=search) | Q(
                title__istartswith=search)) & Q(created_at__gte=yesterday)
        return Q()

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


class AddSongFromUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, song_id):
        try:
            song = Song.objects.get(song_id=song_id)
            if request.user in song.users.all():
                return Response(status=409)
            song.users.add(request.user)
            return Response(status=201)
        except Song.DoesNotExist:
            return Response(status=404)


class UserSongListAPIView(AmountModelViewSet, VKAuthMixin):
    vk_session = None
    uid = None
    ans_stupid = None

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Song.objects.all().order_by('song_id')
    serializer_class = SongListSerializer
    pagination_class = StandardResultsSetPagination

    def get_filter_query(self):
        song_id = self.request.GET.get('song_id', None)
        yesterday = timezone.now() - timezone.timedelta(days=1)
        query = Q(users=self.request.user) & Q(updated_at__gte=yesterday)

        if song_id is not None:
            return query & Q(song_id=song_id)
        return query

    def _as_object(self, i):
        q = self.ans_stupid[i]
        id = i.split("_")[1]
        owner_id = i.split("_")[0]
        sig = q[1][13].split("/")
        sig = sig[2] + "_" + sig[5]
        return Audio_obj(id, owner_id, sig,
                         q[1][3], q[1][4], q[1][5],
                         q[1][14].split(",")[0],
                         self.encode_url, self.vk_session
                         )

    def encode_url(this, url):
        from vk_audio.decoder import decode_audio_url
        return decode_audio_url(url, this.uid)

    def _set_headers(self):
        self.vk_session.http.headers['Upgrade-Insecure-Requests'] = "1"
        self.vk_session.http.cookies.set('remixaudio_background_play_time_', '0')
        self.vk_session.http.cookies.set('remixaudio_background_play_time_limit', '1800')
        self.vk_session.http.cookies.set('remixaudio_show_alert_today', '0')
        self.vk_session.http.cookies.set('remixff', '10')
        self.vk_session.http.cookies.set('remixmaudioq', '')
        self.vk_session.http.cookies.set('remixaudio_date', datetime.datetime.now().date().strftime("%Y-%m-%d"))
        self.vk_session.http.cookies.set('remixmdevice', '1280/800/1/!!-!!!!')
        self.vk_session.http.headers['X-Requested-With'] = 'XMLHttpRequest'

    def _get_vk_songs(self):
        self._set_headers()
        del self.vk_session.http.headers['X-Requested-With']
        text = self.vk_session.http.get(
            f"https://m.vk.com/audio{('s' + str(self.uid)) if self.uid is not None else ''}").text
        self.vk_session.http.headers['X-Requested-With'] = 'XMLHttpRequest'
        all_audio = re.findall(
            '"_cache":(.+?),"soft_filter":true|false,"need_invalid_keys":true|false,"top_len":\d+,', text)
        try:
            all_audio = all_audio[0][:all_audio[0].rfind(',')]
            self.ans_stupid = json.loads(all_audio)
        except:
            self.ans_stupid = json.loads(all_audio[0] if len(all_audio) > 0 and len(all_audio[0]) != 0 else "{}")
        return list(map(self._as_object, self.ans_stupid))

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            self.vk_session = self.try_auth(request.POST, user.vk_login, token=user.auth_token)
            self.uid = self.vk_session.method("users.get")[0]["id"]
            if self.captcha_url:
                return Response({'url': self.captcha_url, 'sid': self.captcha_sid}, status=302)

            audio_list = self._get_vk_songs()
        except Exception as e:
            err_text = 'Cant connect to vk server'
            Log.objects.create(exception=str(e), additional_text=err_text, from_user=user.username)
            return Response(err_text, status=400)

        for track in audio_list:
            try:
                try:
                    song = Song.objects.get(song_id=track.id)
                    if user not in song.users_ignore.all():
                        song.users.add(user)
                    song.download = track.url
                    song.updated_at = now()
                    song.save()
                except Song.DoesNotExist:
                    song = Song.objects.create(
                        song_id=track.id,
                        artist=track.artist,
                        title=track.title,
                        image=track.image,
                        full_id=track.full_id,
                        duration=track.duration,
                        download=track.url,
                    )
                    song.save()
                    song.users.add(user)
            except Exception as e:
                Log.objects.create(exception=str(e), from_user=user.username)
        user.last_songs_update = timezone.now()
        user.save()
        return self.list(request, *args, **kwargs)


class AddNewLinkSongs(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Song.objects.all().order_by('song_id')
    serializer_class = SongListSerializer
