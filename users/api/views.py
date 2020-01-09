from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.db.models import Q
from django.utils.timezone import now

from users.models import User, Relationship, RelationshipStatus
from .serializers import UserSerializer, FriendListSerializer
from core.models import Log


class RelationshipsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_id = request.data.get('user_id', None)
        try:
            if user_id:
                relationship = Relationship.objects.get(from_user=request.user, to_user_id=user_id)
                serializer = FriendListSerializer(relationship)
            else:
                relationship = Relationship.objects.filter(from_user=request.user).all()
                serializer = FriendListSerializer(relationship, many=True)
            return Response({'result': serializer.data}, status=200)
        except Relationship.DoesNotExist:
            return Response({'error': 'Relationships not found'}, status=404)

    def put(self, request):
        user_id = request.data.get('user_id', None)
        status = request.data.get('status', None)

        try:
            rel_status = RelationshipStatus.objects.get(Q(name=status) & ~Q(code=1))
        except RelationshipStatus.DoesNotExist:
            return Response({'error': 'Wrong status'}, status=400)

        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status=404)

        to_user_query = Q(Q(from_user=to_user) & Q(to_user=request.user))
        from_user_query = Q(Q(from_user=request.user) & Q(to_user=to_user))

        try:
            Relationship.objects.get(from_user_query)
            return Response({'error': 'Duplicated'}, status=409)
        except Relationship.DoesNotExist:
            if rel_status == 0:
                try:
                    to_relationship = Relationship.objects.get(to_user_query)
                    if to_relationship.status.code == 0:
                        new_status = RelationshipStatus.objects.get(code=1)
                        Relationship.objects.create(from_user=request.user, to_user=to_user,
                                                    status=new_status, confirmed_at=now())
                        to_relationship.status = new_status
                        to_relationship.confirmed_at = now()
                        to_relationship.save()
                        return Response('Created', status=201)
                    elif to_relationship.status.code == 2:
                        return Response({'error': 'This user has blocked you'}, status=403)
                except Relationship.DoesNotExist:
                    pass
            elif rel_status == 2:
                try:
                    Relationship.objects.get(to_user_query).delete()
                except Relationship.DoesNotExist:
                    pass
            Relationship.objects.create(from_user=request.user, to_user=to_user, status=rel_status)
            return Response('Created', status=201)


class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        request.user.update(data=request.data)
        return Response('Updated', status=200)
