from django.urls import path
from .views import *


urlpatterns = [
    path('list/', UserSongListAPIView.as_view(), name='song_list_url'),
    path('friends/<user_id>', UserSongListAPIView.as_view(), name='friend_song_list_url')
]
