from django.urls import path, include

from .views import UserRegistration, CheckAuth, AppVersion, SignInView

urlpatterns = [
    path('auth/', SignInView.as_view()),
    path('reg/', UserRegistration.as_view()),
    path('app-version/<slug:slug>/', AppVersion.as_view(), name='app_version'),
    path('auth_check/', CheckAuth.as_view()),
    path('songs/', include('songs.api.urls')),
    path('users/', include('users.api.urls')),
    path('youtube/', include('youtube_saver.urls'))
]
