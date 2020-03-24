from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.models import CurrentVersion


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('vk_password', 'password',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')


class CurrentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentVersion
        exclude = ('created_at', 'id')
