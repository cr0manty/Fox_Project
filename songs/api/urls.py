from django.urls import path
from .views import *

search_song = SearchSongsView.as_view({'get': 'list'})
friend_song = FriendsSongsView.as_view({'get': 'list'})

urlpatterns = [
    path('info/', UserSongListAPIView.as_view()),
    path('search/', search_song),
    path('friend-songs/<int:id>', friend_song),
    path('delete_song/<int:song_id>', RemoveSongFromUser.as_view()),
]
