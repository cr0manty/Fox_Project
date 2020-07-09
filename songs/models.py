from django.db import models

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
    ignore_time = models.BooleanField(default=False)

    def ignore_user(self, user):
        if user in self.users.all():
            self.users.remove(user)
            self.users_ignore.add(user)
            super().save()

    def __str__(self):
        return '{} - {}'.format(self.artist, self.title)

