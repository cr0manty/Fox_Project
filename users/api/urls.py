from django.urls import path
from .views import *

search_user = SearchUserView.as_view({'get': 'list'})

urlpatterns = [
    path('profile/', UserAPIView.as_view()),
    path('friends/', RelationshipsAPIView.as_view()),
    path('search/', search_user),
    # path('invites/',),
]
