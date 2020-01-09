import requests

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from threading import Thread

from django.db.models.signals import pre_save
from django.dispatch import receiver
from vk_api import VkApi

from core.models import Log


class User(AbstractUser):
    user_id = models.IntegerField(unique=True, null=True, blank=True)
    vk_login = models.CharField(max_length=255, null=True, blank=True)
    vk_password = models.CharField(max_length=255, null=True)
    can_use_vk = models.BooleanField(default=False)
    image = models.ImageField(blank=True, null=True)

    def vk_auth(self):
        return bool(self.vk_login) and bool(self.vk_password)

    def _check_vk_auth(self):
        try:
            login = self.vk_login if self.vk_login else self.username
            vk_session = VkApi(login=login, password=self.vk_password, config_filename='config.json')
            vk_session.auth()
            if not self.can_use_vk or not self.vk_auth():
                self.user_id = vk_session.method('users.get')[0]['id']
                self.vk_login = login
                self.can_use_vk = True
                super().save()
            return True
        except requests.exceptions.ConnectionError as e:
            Log.objects.create(exception=str(e))
            return False

    def vk_auth_checked(self):
        timeout_thread = Thread(target=self._check_vk_auth, daemon=True)
        timeout_thread.start()
        timeout_thread.join(timeout=10)
        self.can_use_vk = timeout_thread.isAlive()
        super().save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        UserLocation.objects.create(user=self)
        self.vk_auth_checked()

    def set_vk_info(self, user_id):
        self.vk_login = self.username
        self.can_use_vk = True
        self.user_id = user_id
        super().save()

    def update(self, data):
        self.username = data.get('username', self.username)
        self.first_name = data.get('first_name', self.first_name)
        self.last_name = data.get('last_name', self.last_name)
        self.email = data.get('email', self.email)
        self.user_id = data.get('user_id', self.user_id)
        self.image = data.get('image', self.image)
        self.vk_password = data.get('vk_password', self.vk_password)
        self.vk_login = data.get('vk_login', self.vk_login)
        super().save()

    def __str__(self):
        return self.username


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=10, null=True)
    ip = models.CharField(max_length=15, null=True)
    need_proxy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.get_location()
        super().save(*args, **kwargs)

    def get_location(self):
        user_info = requests.get(settings.USER_LOCATION_URL_JSON).json()
        self.location = user_info.get('Country', None)
        self.ip = user_info.get('IP', None)

        if self.location == 'UA':
            self.need_proxy = True

    def __str__(self):
        return self.user.username


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
