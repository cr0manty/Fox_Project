from django.contrib import admin

from youtube_saver.models import YoutubePosts, YoutubeFormats


@admin.register(YoutubePosts)
class YoutubePostsAdmin(admin.ModelAdmin):
    pass


admin.site.register(YoutubeFormats)
