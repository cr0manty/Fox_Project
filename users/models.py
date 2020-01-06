import requests

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from threading import Thread
from vk_api import VkApi


class User(AbstractUser):
    user_id = models.IntegerField(unique=True, null=True, blank=True)
    vk_login = models.CharField(max_length=255, null=True, blank=True)
    vk_password = models.CharField(max_length=255, null=True)
    can_use_vk = models.BooleanField(default=False)
    image = models.ImageField(blank=True, null=True)
    friends = models.ManyToManyField('self', blank=True, related_name='friends')

    def vk_auth(self):
        return bool(self.vk_login) and bool(self.vk_password)

    def _check_vk_auth(self):
        try:
            login = self.vk_login if self.vk_login else self.username
            vk_session = VkApi(login=login, password=self.vk_password, config_filename='config.json')
            vk_session.auth()
            self.user_id = vk_session.method('users.get')[0]['id']
        except requests.exceptions.ConnectionError as e:
            print(e)

    def vk_auth_checked(self):
        timeout_thread = Thread(target=self._check_vk_auth, daemon=True)
        timeout_thread.start()
        timeout_thread.join(timeout=10)
        self.can_use_vk = timeout_thread.isAlive()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        UserLocation.objects.create(user=self)
        self.vk_auth_checked()

    def __str__(self):
        return self.username


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=10, null=True)
    ip = models.CharField(max_length=15, null=True)
    need_proxy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.get_location()

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


class FriendList(models.Model):
    user = models.ForeignKey(User, related_name='main_user', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='user_friend', on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True)

    def __str__(self):
        return '{} friends'.format(self.user.username)
