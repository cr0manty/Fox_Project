from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from users.models import User, FriendList


class UserSongListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id=None):
        user = request.user
        user_friends = FriendList.objects.filter(user=user).all()


    def post(self, request, user_id=None):
        user = request.user
        if user_id:
            try:
                user = FriendList.objects.get(user=user, friend__user_id=user_id)
            except FriendList.DoesNotExist:
                return Response({'error': 'No relationships with this user'}, status=403)
