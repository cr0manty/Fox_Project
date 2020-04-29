from django.contrib import admin

from youtube_saver.models import YoutubePosts


@admin.register(YoutubePosts)
class YoutubePostsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


