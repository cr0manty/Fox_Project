from rest_framework import serializers
from django.contrib.auth import get_user_model

from home.models import MyApp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('vk_password', 'password',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')


class MyAppSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MyApp
        fields = ('title', 'details', 'version', 'url')

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.get_absolute_url())
