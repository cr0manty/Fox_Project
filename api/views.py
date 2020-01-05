from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from vk_api import VkApi
from threading import Thread
from requests.exceptions import ConnectionError

from .serializers import UserSerializer

User = get_user_model()


def vk_auth(user):
    try:
        login = user.vk_login if user.vk_login else user.username
        vk_session = VkApi(login=login, password=user.vk_password, config_filename='config.json')
        vk_session.auth()
    except ConnectionError as e:
        print(e)


class CheckAuth(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        return Response(status=200)

    def put(self, request):
        timeout_thread = Thread(target=vk_auth, args=(request.user,))
        timeout_thread.start()
        timeout_thread.join(timeout=15)
        if timeout_thread.isAlive():
            return Response(status=401)
        return Response(status=200)


class UserRegistration(APIView):
    def post(self, request):
        VALID_USER_FIELDS = [user.name for user in User._meta.fields]
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            user_data = {field: data for (field, data) in request.data.items() if field in VALID_USER_FIELDS}
            if not user_data.get('vk_password', None):
                user_data.update({'vk_password': user_data.get('password')})
            user = User.objects.create_user(
                **user_data
            )
            return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
