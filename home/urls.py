from django.urls import path, include
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('app/<slug:slug>', AppView.as_view(), name='app_view'),
    path('short/<slug>', url_shorter, name='short_url'),
]
