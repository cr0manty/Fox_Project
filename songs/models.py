from django.conf import settings
from django.db import models
from django_rq import get_scheduler, job

from django.utils import timezone
from vk_api import VkApi
from vk_audio import audio

from core.models import RQLog
from core.models import Log
from users.models import User


class Song(models.Model):
    song_id = models.IntegerField(unique=True)
    artist = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    full_id = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    users = models.ManyToManyField(User, blank=True, related_name='song_users')
    users_ignore = models.ManyToManyField(User, blank=True, related_name='song_users_ignore')
    duration = models.IntegerField(default=0)
    download = models.TextField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def ignore_user(self, user):
        if user in self.users.all():
            self.users.remove(user)
            self.users_ignore.add(user)
            super().save()

    def __str__(self):
        return '{} - {}'.format(self.artist, self.title)


class SongsUpdateRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True)

    def update(self, pause=None):
        if settings.USE_REDIS:
            pause = timezone.now() if pause else pause
            scheduler = get_scheduler('default')
            scheduler.enqueue_at(pause, update_user_songs, user=self.user)
        else:
            update_user_songs(self.user)
        self.updated_time = pause if pause else timezone.now()
        super(SongsUpdateRequest, self).save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            request = SongsUpdateRequest.objects.latest('id')
            now = timezone.now()
            delta = timezone.timedelta(minutes=5)

            pause = now if request.updated_time < now - delta else now + delta
            self.update(pause=pause)
        except SongsUpdateRequest.DoesNotExist:
            self.update()

@job
def update_user_songs(user):
    try:
        vk_session = VkApi(login=user.vk_login, password=user.vk_password, config_filename='config.json')
        vk_session.auth()
        audio_obj = audio(vk_session)
        song_list = audio_obj.get()
    except Exception as e:
        RQLog.objects.create(exception_text=str(e), from_user=user.username, is_exception=True)
    else:
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
