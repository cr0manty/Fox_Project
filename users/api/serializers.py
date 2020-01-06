from rest_framework import serializers

from users.models import User, FriendList


class FriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendList
        fields = (

        )


class UserSerializer(serializers.ModelSerializer):
    vk_auth = serializers.ReadOnlyField()
    lookup_field = 'username'

    class Meta:
        model = User
        exclude = ('vk_password', 'vk_login', 'password',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser')
