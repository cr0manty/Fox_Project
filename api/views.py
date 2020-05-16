from datetime import datetime

import django_rq
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from home.models import MyApp
from users.tasks import update_users_song_list
from .serializers import UserSerializer, MyAppSerializer

User = get_user_model()


class AppVersion(APIView):
    def get(self, request, slug):
        app = get_object_or_404(MyApp, slug=slug)
        serializer = MyAppSerializer(app, context={"request": request})
        return Response(serializer.data, status=200)


class CheckAuth(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        return Response(status=200)


class UserRegistration(APIView):
    def post(self, request):
        VALID_USER_FIELDS = [user.name for user in User._meta.fields]
        serialized = UserSerializer(data=request.data, context={'request': request})
        if serialized.is_valid():
            user_data = {field: data for (field, data) in request.data.items() if field in VALID_USER_FIELDS}
            if not user_data.get('vk_password', None):
                user_data.update({'vk_password': user_data.get('password')})
            if not user_data.get('vk_login', None):
                user_data.update({'vk_login': user_data.get('username')})
            user = User.objects.create_user(
                **user_data
            )
            serialized = UserSerializer(instance=user, context={'request': request})
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        update_users_song_list.delay()
        return super().post(request, *args, **kwargs)
