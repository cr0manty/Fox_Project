from django.urls import path
from .views import *

search_user = UserAPIView.as_view({'get': 'list'})

user_view = UserAPIView.as_view({
    'get': 'retrieve', 'put': 'update', 'post': 'create'
})

urlpatterns = [
    path('profile/', user_view),
    path('friends/', RelationshipsAPIView.as_view()),
    path('search/', search_user),
    # path('invites/',),
]
