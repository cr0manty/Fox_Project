from rest_framework import serializers

from youtube_saver.models import YoutubeFormats, YoutubePosts


class YoutubeFormatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeFormats
        fields = '__all__'

    def save(self, attrs):
        return {
            'url': attrs['url'],
            'size': attrs['filesize'],
            'file_type': 'song' if attrs['fps'] is None else 'video',
            'format': attrs['format_note'],
        }
    def validate(self, attrs):
        return attrs


class YoutubePostsSerializer(serializers.ModelSerializer):
    formats = YoutubeFormatsSerializer(many=True, read_only=True)

    class Meta:
        model = YoutubePosts
        fields = '__all__'

    def validate(self, attrs):
        attrs['image'] = self.initial_data.get('thumbnail')

        index = attrs['webpage_url'].find('=')
        attrs['slug'] = attrs['webpage_url'][index + 1:]
        return attrs

    def save(self, **kwargs):
        formats = self.initial_data.get('formats')

        obj = YoutubePosts.objects.create(**self.validated_data)
        for format in formats:
            format_obj = YoutubeFormatsSerializer(data=format)
            if format_obj.is_valid():
                format_obj.save()
                obj.formats.add(format_obj)
        return obj
