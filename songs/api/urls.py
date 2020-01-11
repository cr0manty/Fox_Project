from django.urls import path
from .views import *


urlpatterns = [
    path('info/', UserSongListAPIView.as_view(), name='song_list_url'),
]
