from django.contrib import admin

from youtube_saver.models import YoutubePosts, DownloadYoutubeMP3ShortLink


@admin.register(YoutubePosts)
class YoutubePostsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


@admin.register(DownloadYoutubeMP3ShortLink)
class YoutubePostsAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
