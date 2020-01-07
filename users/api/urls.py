from django.urls import path
from .views import *


urlpatterns = [
    path('profile/', UserAPIView.as_view()),
    path('friends/', RelationshipsAPIView.as_view()),
    # path('invites/',),
]
