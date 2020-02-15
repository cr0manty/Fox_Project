from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .serializers import UserSerializer

User = get_user_model()


def app_version(request):
    return HttpResponse(settings.APP_VERSION, status=200)


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
