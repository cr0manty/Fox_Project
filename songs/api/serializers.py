from rest_framework import serializers

from songs.models import Song


class SongListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        exclude = ('users', 'id')
