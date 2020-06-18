import re
import uuid

import youtube_dl
from django.conf import settings
from django.utils import timezone

from core.models import TelegramBotLogs
from youtube_saver.models import DownloadYoutubeMP3ShortLink


def get_download_url(message, func=None, **kwargs):
    try:
        urls = re.findall(settings.YOUTUBE_REGEX, message.text)
        if urls:
            with youtube_dl.YoutubeDL(settings.YOUTUBE_DOWNLOAD_PARAMS) as ydl:
                url_param = urls[0].find('&')
                result = ydl.extract_info(urls[0][:url_param] if url_param != -1 else urls[0], download=False)
                true_song = []

                if func is not None:
                    func(**kwargs)

                for result_format in result['formats']:
                    if result_format['format_note'] == 'tiny':
                        true_song.append({
                            'format': result_format['format_id'],
                            'url': result_format['url']
                        })

                    if result_format['format_note'].startswith('DASH') and result_format['format_note'].find(
                            'audio') != -1:
                        true_song.append({
                            'format': result_format['format_id'],
                            'url': result_format['fragment_base_url']
                        })

                if true_song:
                    best_audio = sorted(true_song, key=lambda item: item['format'])[-1]
                    url = create_short_url(result, best_audio, message.from_user.username)
                    return '{} \n\nThis link is open just for 24 hours'.format(url.get_absolute_url())
                TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, log_type=2))
                return 'Not Found'
    except Exception as e:
        TelegramBotLogs.objects.create(**TelegramBotLogs.get_kwargs(message, e=e))


def create_short_url(result, song, username, slug_length=8):
    now = timezone.now()
    try:
        link = DownloadYoutubeMP3ShortLink.objects.get(username=username, video_slug=result['channel_id'])
        link.created_at = now
        link.url = song.get('url')
        link.save()
        return link
    except DownloadYoutubeMP3ShortLink.DoesNotExist:
        pass

    slug = str(uuid.uuid4())[:slug_length]
    try:
        link = DownloadYoutubeMP3ShortLink.objects.get(slug=slug)
        yesterday = now - timezone.timedelta(days=1)
        if link.created_at <= yesterday:
            link.delete()
        return create_short_url(result, song, username, slug_length + 2)
    except DownloadYoutubeMP3ShortLink.DoesNotExist:
        return DownloadYoutubeMP3ShortLink.objects.create(url=song.get('url'), title=result.get('title'),
                                                          original_url=result['webpage_url'],
                                                          slug=slug, username=username,
                                                          duration=result.get('duration'),
                                                          video_slug=result['channel_id'])
