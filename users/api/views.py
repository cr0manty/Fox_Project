from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.db.models import Q
from django.utils.timezone import now

from users.models import User, Relationship, RelationshipStatus
from .serializers import UserSerializer, FriendListSerializer


class SearchUserView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = UserSerializer

    def get_query(self):
        search = self.request.GET.get('search')
        query = Q()

        if search:
            query = Q(Q(first_name__istartswith=search) | Q(
                last_name__istartswith=search) | Q(username__istartswith=search))
        return query

    def get_queryset(self):
        return User.objects.filter(self.get_query()).exclude(id=self.request.user.id)


class RelationshipsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_id = request.GET.get('user_id', None)
        status_code = request.GET.get('status_code', None)
        query = Q(from_user=request.user)

        if status_code:
            if status_code != -2:
                query &= Q(status__code=status_code)
        else:
            query &= ~Q(status__code=3)
        try:
            if user_id is not None:
                relationship = Relationship.objects.get(query & Q(to_user_id=user_id))
                serializer = FriendListSerializer(relationship)
            else:
                relationship = Relationship.objects.filter(query).order_by('-status__code').all()
                serializer = FriendListSerializer(relationship, many=True)
            return Response({'result': serializer.data}, status=200)
        except Relationship.DoesNotExist:
            return Response({'error': 'Relationships not found'}, status=404)

    def put(self, request):
        user_id = int(request.data.get('user_id', 0))
        status = request.data.get('status', None)

        try:
            rel_status = RelationshipStatus.objects.get(Q(name=status) & ~Q(code=1))
        except RelationshipStatus.DoesNotExist:
            return Response({'error': 'Wrong status'}, status=400)

        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status=404)

        to_user_query = Q(from_user=to_user) & Q(to_user=request.user)
        from_user_query = Q(from_user=request.user) & Q(to_user=to_user)

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
                    elif to_relationship.status.code == 3:
                        return Response({'error': 'This user has blocked you'}, status=403)
                except Relationship.DoesNotExist:
                    pass
            elif rel_status == 3:
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
        user_id = int(request.GET.get('user_id', 0))
        try:
            user = User.objects.get(id=user_id) if user_id else request.user
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': "User doesn't exist"}, status=404)

    def post(self, request):
        request.user.update(data=request.data)
        return Response('Updated', status=201)

    def put(self, request):
        request.user.set_vk_info(data=request.data)
        return Response('Updated', status=201)
