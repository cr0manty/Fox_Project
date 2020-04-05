from django.urls import path, include
from .views import YoutubeApiView, YoutubeView

youtube_list = YoutubeView.as_view({'get': 'list'})
youtube_info = YoutubeView.as_view({'get': 'retrieve'})
youtube_find = YoutubeApiView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', youtube_find),
    path('info/', include([
        path('', youtube_list),
        path('<slug:slug>/', youtube_info),
    ])),
]
