import os
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from vk_api import VkApi
from uuid import uuid4

from core.models import VKAuthMixin
from home.models import MyApp
from songs.models import update_user_songs
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
        serialized = UserSerializer(data=request.data, context={'request': request})
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        if settings.USE_REDIS and request.data.get('username'):
            try:
                user = User.objects.get(username=request.data['username'], can_use_vk=True)
                update_user_songs.delay(user=user)
            except User.DoesNotExist:
                pass
        return super().post(request, *args, **kwargs)


class SignInVkView(APIView, VKAuthMixin):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = request.user
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return Response('Bad', status=403)

        session = self.try_auth(request.POST, username, password)
        if not session:
            return Response('Bad', status=403)

        if self.captcha_url:
            dir_name = 'media/captcha'
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)

            img_data = requests.get(self.captcha_url)
            filename = '{}/username_{}.jpeg'.format(dir_name, uuid4())

            with open(filename, 'wb') as handler:
                handler.write(img_data.content)
            protocol = 'https' if request.is_secure == True else 'http'
            file_url = '{}://{}/{}'.format(protocol, request.META['HTTP_HOST'], filename)
            return Response({'url': file_url, 'sid': self.captcha_sid}, status=302)

        user.vk_login = username
        user.vk_auth_token = session.token.get('access_token')
        user.can_use_vk = True
        user.save()

        return Response('Success', status=200)
