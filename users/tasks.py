from django.utils.timezone import now
from celery.task import periodic_task
from celery.schedules import crontab

from vk_music.celery import app
from core.utils import get_vk_auth, get_vk_songs

from .models import User
from core.models import Log
from songs.models import Song


@periodic_task(name='update_users_song_list', ignore_result=True, run_every=(crontab(hour=0, minute=0)))
def update_users_song_list():
    users = User.objects.filter(can_use_vk=True).all()
    for user in users:
        update_user_songs.delay(user)


@app.task(name="update_user_song")
def update_user_songs(user):
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
            Log.objects.create(exception=str(e), from_user=user.username)
