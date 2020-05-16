from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from .views import YoutubeApiView, TelegramBotView, set_webhook

youtube_find = YoutubeApiView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', youtube_find),
    path('webhook/<token>', csrf_exempt(TelegramBotView.as_view()), name='webhook'),
    path('update-webhook/', staff_member_required(set_webhook), name='update_webhook'),
]
