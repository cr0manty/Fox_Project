from django.urls import path, include
from .views import YoutubeApiView

youtube_list = YoutubeApiView.as_view({'get': 'list', 'post': 'create'})
youtube_info = YoutubeApiView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', youtube_list),
    path('<slug:slug>/', youtube_info),
]
