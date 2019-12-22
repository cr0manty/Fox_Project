from rest_framework import serializers

from songs.models import Song


class SongListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ('song_id', 'artist', 'name',
                  'duration', 'download', 'posted_at')
