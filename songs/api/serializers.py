import random
from rest_framework import serializers

from songs.models import Song


class SongListSerializer(serializers.ModelSerializer):
    in_my_list = serializers.SerializerMethodField()

    class Meta:
        model = Song
        exclude = ('users', 'id', 'users_ignore', 'posted_at', 'updated_at')
        read_only = ('in_my_list',)
        extra_kwargs = {'song_id': {'required': False}}

    def get_in_my_list(self, song):
        request = self.context.get('request')
        return 1 if request.user in song.users.all() else 0

    def validate(self, attrs):
        cleaned_data = super().validate(attrs)
        download = cleaned_data.get('download')

        if cleaned_data.get('song_id') is None:
            exist = True
            num = 0
            while exist:
                num = random.randint(1, 1000000)
                try:
                    Song.objects.get(song_id=num)
                except Song.DoesNotExist:
                    exist = False
            cleaned_data['song_id'] = num

        if not download.startswith('http') or not download.endswith('.mp3'):
            raise serializers.ValidationError('Only a direct link to the file is allowed')

        if not cleaned_data.get('title'):
            raise serializers.ValidationError('Title filed is required')

        if not cleaned_data.get('artist'):
            raise serializers.ValidationError('Artist filed is required')

        if not cleaned_data.get('duration'):
            raise serializers.ValidationError('Duration filed is required')

        if Song.objects.filter(artist=cleaned_data.get('artist'), title=cleaned_data.get('title'),
                               download=download).count() > 0:
            raise serializers.ValidationError('Song already exist')

        return cleaned_data
    
    def save(self, **kwargs):
        song = super().save(**kwargs)
        song.users.add(self.context.get('request').user)
        self.fields.serializer.data['in_my_list'] = 1
