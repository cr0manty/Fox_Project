import django_rq

from django.utils import timezone

from core.utils import get_vk_auth, get_vk_songs

from .models import User
from core.models import RQLog
from songs.models import Song


@django_rq.job
def update_users_song_list():
    RQLog.objects.create(from_user='test')
    for user in User.objects.filter(can_use_vk=True):
        RQLog.objects.create(from_user=user.username)
        update_user_songs.delay(user)


@django_rq.job
def update_user_songs(user):
    song_list = get_vk_songs(get_vk_auth(user))
    for track in song_list:
        try:
            try:
                song = Song.objects.get(song_id=track.get('id'))
                if user not in song.users_ignore.all():
                    song.users.add(user)
                song.download = track['url']
                song.updated_at = timezone.now()
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
        except Exception as e:
            RQLog.objects.create(exception_text=str(e), from_user=user.username, is_exception=True)
