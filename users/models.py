from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

import requests


class User(AbstractUser):
    user_id = models.IntegerField(unique=True, null=True)
    dump_password = models.CharField(max_length=255, null=True)
    image = models.ImageField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        UserLocation.objects.create(user=self)


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=10, null=True)
    ip = models.CharField(max_length=15, null=True)
    need_proxy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_location(self):
        user_info = requests.get(settings.USER_LOCATION_URL_JSON).json()
        self.location = user_info.get('Country', None)
        self.ip = user_info.get('IP', None)
        
        if self.location == 'UA':
            self.need_proxy = True


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
