from django.urls import path
from .views import *


message = MessageViewSet.as_view({'get': 'list', 'post': 'create'})

urlpatterns = [
    path('friend_messages/<int:user_id>', message),
]
