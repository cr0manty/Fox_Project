from rest_framework import serializers

from songs.models import Song


class SongListSerializer(serializers.ModelSerializer):
    in_my_list = serializers.SerializerMethodField()

    class Meta:
        model = Song
        exclude = ('users', 'id', 'users_ignore', 'posted_at', 'updated_at')

    def get_in_my_list(self, song):
        request = self.context.get('request')
        return 1 if request.user in song.users.all() else 0
