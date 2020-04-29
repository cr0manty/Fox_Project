from rest_framework import serializers
from django.contrib.auth import get_user_model

from home.models import MyApp, AppVersions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('vk_password', 'password',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')


class MyAppSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    update_details = serializers.SerializerMethodField()

    class Meta:
        model = MyApp
        fields = ('title', 'update_details', 'version', 'url')

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri('home')

    def get_version(self, obj):
        last = obj.last_version
        return last.version if last else '0.0.0'

    def get_update_details(self, obj):
        last = obj.last_version
        return last.version if last else 'Your version is out of date, please upgrade to a new version'
