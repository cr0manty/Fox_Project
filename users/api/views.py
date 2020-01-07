from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from users.models import User, FriendList
from .serializers import UserSerializer

from core.models import Log


class UserFriendListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                e = 'No relationships with {}'.format(user_id)
                Log.objects.create(exception=e)
                return Response({'error': e}, status=403)

    def post(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                e = 'No relationships with {}'.format(user_id)
                Log.objects.create(exception=e)
                return Response({'error': e}, status=403)


class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
