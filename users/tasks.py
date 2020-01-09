from django.utils.timezone import now, timedelta

from vk_music.celery import app
from core.utils import get_vk_auth, get_vk_songs

from .models import User
from core.models import Log
from songs.models import Song


@app.task(name="user_song_list.get_from_vk_period")
def get_songs():
    users = User.objects.filter(can_use_vk=True).all()
    for user in users:
        pass


@app.task(name="user_song_list.get_from_vk")
def get_songs(user):
    song_list = get_vk_songs(get_vk_auth(user))
    for track in song_list:
        try:
            try:
                song = Song.objects.get(song_id=track.get('id'))
                song.users.add(user)
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
        except Exception as e:
            Log.objects.create(exception=str(e))