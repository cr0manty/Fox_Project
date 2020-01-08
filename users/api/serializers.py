from rest_framework import serializers

from users.models import User, Relationship


class FriendListSerializer(serializers.ModelSerializer):
    from_user = serializers.SlugRelatedField(many=False, slug_field="username", read_only=True)
    from_user_id = serializers.SlugRelatedField(many=False, slug_field="id", read_only=True)
    to_user = serializers.SlugRelatedField(many=False, slug_field="username", read_only=True)
    to_user_id = serializers.SlugRelatedField(many=False, slug_field="id", read_only=True)
    status = serializers.SlugRelatedField(many=False, slug_field="code", read_only=True)

    class Meta:
        model = Relationship
        fields = ('from_user', 'from_user_id', 'to_user', 'to_user_id',
                  'status', 'created_at', 'confirmed_at')


class UserSerializer(serializers.ModelSerializer):
    vk_auth = serializers.ReadOnlyField()
    lookup_field = 'username'

    class Meta:
        model = User
        exclude = ('vk_password', 'vk_login', 'password',
                   'user_permissions', 'groups', 'is_active',
                   'is_superuser', 'last_login')
