from rest_framework import serializers

from songs.models import Song


class SongListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, slug_field="username", read_only=True)

    class Meta:
        model = Song
        fields = ('artist', 'name', 'duration',
                  'user', 'download')
