from django.urls import reverse
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from home.models import MyApp


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 25


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        extra_kwargs = {
            'password': {'write_only': True},
        }
        exclude = ('user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')

    def create(self, validated_data):
        return get_user_model().objects.create_user(
            **validated_data
        )


class MyAppSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    update_details = serializers.SerializerMethodField()

    class Meta:
        model = MyApp
        fields = ('title', 'update_details', 'version', 'url')

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('home'))

    def get_version(self, obj):
        last = obj.last_version
        return last.version if last else '0.0.0'

    def get_update_details(self, obj):
        last = obj.last_version
        return last.version.update_details if last else 'Your version is out of date, please upgrade to a new version'
