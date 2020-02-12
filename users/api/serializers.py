from rest_framework import serializers

from users.models import User, Relationship


class UserSerializer(serializers.ModelSerializer):
    lookup_field = 'username'

    class Meta:
        model = User
        exclude = ('vk_password', 'password', 'vk_login',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')


class FriendListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'image', 'is_staff')


class FriendListSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(many=False, read_only=True)
    status = serializers.SlugRelatedField(many=False, slug_field="code", read_only=True)

    class Meta:
        model = Relationship
        fields = ('to_user', 'status',
                  'created_at', 'confirmed_at')
