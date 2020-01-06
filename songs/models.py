from django.db import models

from users.models import User


class Song(models.Model):
    song_id = models.IntegerField(unique=True, null=True)
    artist = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    users = models.ManyToManyField(User, blank=True)
    duration = models.IntegerField(default=0)
    download = models.TextField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.artist, self.name)
