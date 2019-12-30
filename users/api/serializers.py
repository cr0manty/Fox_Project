from rest_framework import serializers, status
from rest_framework.response import Response

from users.models import User, FriendList


class FriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendList
        fields = (

        )


class UserSerializer(serializers.ModelSerializer):
    lookup_field = 'username'

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'is_staff', 'date_joined',
                  'user_id', 'image')
        read_only_fields = ('id', 'is_staff', 'date_joined')
