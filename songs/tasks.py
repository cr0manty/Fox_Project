import datetime

from django_rq import job
from vk_api import VkApi

from core.models import RQLog
from songs.models import Song
from songs.utils import GetSongUtils


@job('default', timeout=1000)
def job_get_user_songs(user):
    vk_session = VkApi(login=user.vk_login, config_filename='config.json', token=user.vk_auth_token)
    vk_session.auth(token_only=True)
    uid = vk_session.method("users.get")[0]["id"]

    try:
        get_songs = GetSongUtils(vk_session, uid)
        audio_list = get_songs.get_vk_songs()
    except Exception as e:
        RQLog.objects.create(exception=str(e), additional_text='Cant connect to vk server', from_user=user.username)
        return

    for track in audio_list:
        try:
            try:
                song = Song.objects.get(song_id=track.id)
                if user not in song.users_ignore.all():
                    song.users.add(user)
                song.download = track.url
                song.updated_at = datetime.datetime.now()
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
            RQLog.objects.create(exception=str(e), from_user=user.username)
    user.last_songs_update = datetime.datetime.now()
    user.save()


def get_user_songs(user):
    job_get_user_songs.delay(user)
