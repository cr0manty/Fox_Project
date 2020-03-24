from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserRegistration, CheckAuth, AppVersion

urlpatterns = [
    path('auth/', obtain_auth_token),
    path('reg/', UserRegistration.as_view()),
    path('auth_check/', CheckAuth.as_view()),
    path('songs/', include('songs.api.urls')),
    path('users/', include('users.api.urls')),
    path('current-app-version/', AppVersion.as_view(), name='app_version')
]
