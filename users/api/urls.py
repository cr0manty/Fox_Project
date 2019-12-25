from django.urls import path
from .views import *


urlpatterns = [
    path('profile/', UserAPIView.as_view()),
    # path('friends/<user_id>', ),
    # path('invites/',),
]
