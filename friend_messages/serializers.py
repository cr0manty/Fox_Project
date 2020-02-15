from rest_framework import serializers

from friend_messages.models import Message
from users.models import User


class UserMessageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'image', 'id')

    def get_image(self, user):
        request = self.context.get('request')
        image = user.image.url
        return request.build_absolute_uri(image)


class MessageSerializer(serializers.ModelSerializer):
    from_user = UserMessageSerializer()
    to_user = UserMessageSerializer()

    class Meta:
        model = Message
        fields = ('id', 'from_user', 'to_user', 'send_at', 'message', 'silence')
