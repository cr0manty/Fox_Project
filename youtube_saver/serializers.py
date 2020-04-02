from rest_framework import serializers
from rest_framework.fields import empty

from youtube_saver.models import YoutubeFormats, YoutubePosts


class YoutubeFormatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeFormats
        fields = '__all__'

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = {
            'url': data['url'],
            'size': data['filesize'],
            'file_type': 'song' if data['fps'] is None else 'video',
            'format': data['format_note'],
        }
        return value


class YoutubePostsSerializer(serializers.ModelSerializer):
    formats = YoutubeFormatsSerializer(many=True)

    class Meta:
        model = YoutubePosts
        fields = '__all__'

    def validate(self, attrs):
        attrs['image'] = self.initial_data.get('thumbnail')

        index = attrs['webpage_url'].find('=')
        attrs['slug'] = attrs['webpage_url'][index + 1:]
        return attrs

    def create(self, validated_data):
        formats = validated_data.pop('formats')
        video, _ = YoutubePosts.objects.get_or_create(**validated_data)

        for video_format in formats:
            video_obj, _ = YoutubeFormats.objects.get_or_create(**video_format)
            video.formats.add(video_obj)
        return video
