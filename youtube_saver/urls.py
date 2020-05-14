from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from .views import YoutubeApiView, TelegramBotView

youtube_find = YoutubeApiView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', youtube_find),
    path('webhook/<token>', csrf_exempt(TelegramBotView.as_view()), name='telegram_webhook'),
]
