from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('vk_password', 'password',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')
