from django.db import models

from users.models import User


class Song(models.Model):
    song_id = models.IntegerField(unique= True, null=True)
    artist = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    users = models.ManyToManyField(User, null=True)
    duration = models.IntegerField(default=0)
    download = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

