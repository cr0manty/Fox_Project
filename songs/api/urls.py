from django.urls import path
from .views import *

search_song = SearchSongsView.as_view({'get': 'list'})
friend_song = FriendsSongsView.as_view({'get': 'list'})
song_list = UserSongListAPIView.as_view({'get': 'list', 'post': 'create'})
add_new_song = AddNewLinkSongs.as_view({'post': 'create'})

urlpatterns = [
    path('info/', song_list),
    path('search/', search_song),
    path('friend-songs/<int:id>/', friend_song),
    path('delete_song/<int:song_id>/', RemoveSongFromUser.as_view()),
    path('add_song/<int:song_id>/', AddSongFromUser.as_view()),
    path('add-new-song/', add_new_song),
    path('image-cover/', add_new_song),
]
