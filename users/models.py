import urllib.request

from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models import Log


class User(AbstractUser):
    user_id = models.IntegerField(unique=True, null=True, blank=True)
    vk_login = models.CharField(max_length=255, null=True, blank=True)
    vk_password = models.CharField(max_length=255, null=True, blank=True)
    can_use_vk = models.BooleanField(default=False)
    image = models.ImageField(upload_to='user_image', default='user-default.png')
    last_songs_update = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image.name.startswith('http'):
            name = self.image.name[self.image.name.rfind('/') + 1:]
            img = urllib.request.urlopen(self.image.name)
            self.image.save(name, img, save=True)
        super().save(*args, **kwargs)

    def update(self, data):
        password = data.get('password', None)
        if password:
            self.set_password(password)

        self.first_name = data.get('first_name', self.first_name)
        self.last_name = data.get('last_name', self.last_name)
        self.email = data.get('email', self.email)
        self.image = data.get('image', self.image)
        self.username = data.get('username', self.username)
        self.save()

    def __str__(self):
        return self.username


class Proxy(models.Model):
    ip = models.CharField(max_length=32)
    port = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_valid = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)

    def check_for_valid(self):
        return self.checked

    def save(self, *args, **kwargs):
        self.check_for_valid()
        super().save(*args, **kwargs)


class RelationshipStatus(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = 'Relationship Status'
        verbose_name_plural = 'Relationships Statuses'

    def __str__(self):
        return self.name


class Relationship(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    status = models.ForeignKey(RelationshipStatus, related_name='status',
                               on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} -> {} - {}'.format(self.from_user.username, self.to_user.username, self.status.name)
