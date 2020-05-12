from rest_framework import serializers
from rest_framework.fields import empty

from youtube_saver.models import YoutubePosts


class YoutubeFormatsSerializer(serializers.Serializer):
    FILE_TYPES = (
        ('song', 'Song'),
        ('video', 'Video'),
        ('video_song', 'Video with Audio')
    )
    url = serializers.CharField()
    size = serializers.IntegerField(default=0)
    file_type = serializers.CharField(max_length=10, default='song')
    format = serializers.CharField(max_length=128)

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        if data.get('fragment_base_url'):
            video = data['format'].find('audio') == -1
            format_index = data['format'].find(' - ')
            value = {
                'url': data['fragment_base_url'],
                'size': data['filesize'],
                'file_type': 'video' if video else 'song',
                'format': data['format'][format_index + 3:data['format'].find(' (')] if video else data['format'][
                                                                                                   :format_index],
            }
        else:
            value = {
                'url': data['url'],
                'size': data['filesize'],
                'file_type': 'song' if data['fps'] is None else 'video',
                'format': data['format_note'],
            }
            value['file_type'] = 'video_song' if value['format'].endswith('p') and value['file_type'] == 'song' else \
            value[
                'file_type']

        return value


class YoutubePostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubePosts
        exclude = ('id',)

    def validate(self, attrs):
        attrs['image'] = self.initial_data.get('thumbnail')

        index = attrs['webpage_url'].find('=')
        attrs['slug'] = attrs['webpage_url'][index + 1:]
        return attrs

    def create(self, validated_data):
        try:
            return YoutubePosts.objects.get(slug=validated_data['slug'])
        except YoutubePosts.DoesNotExist:
            video = YoutubePosts.objects.create(**validated_data)
            return video
