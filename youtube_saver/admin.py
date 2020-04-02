from django.contrib import admin

from youtube_saver.models import YoutubePosts, YoutubeFormats


@admin.register(YoutubePosts)
class YoutubePostsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


@admin.register(YoutubeFormats)
class YoutubeFormatsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
