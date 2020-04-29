from django.urls import path, include
from .views import YoutubeApiView

youtube_find = YoutubeApiView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', youtube_find),
]
