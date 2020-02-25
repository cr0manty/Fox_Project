from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.db.models import Q
from django.utils.timezone import now

from users.models import User, Relationship, RelationshipStatus
from .serializers import UserSerializer, FriendListSerializer


class RelationshipsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        # TODO
        user_id = request.GET.get('user_id', None)
        status_code = request.GET.get('status_code', None)
        query = Q(Q(from_user=request.user) | Q(to_user=request.user))

        if status_code:
            if status_code != 'all':
                query &= Q(status__code=status_code)
        else:
            query &= ~Q(status__code=3) & ~Q(status__code=4)
        try:
            if user_id is not None:
                relationship = Relationship.objects.get(query & Q(to_user_id=user_id))
                serializer = FriendListSerializer(relationship, context={'request': request})
            else:
                relationship = Relationship.objects.filter(query).order_by('-status__code').all()
                serializer = FriendListSerializer(relationship, many=True, context={'request': request})
            return Response({'result': serializer.data}, status=200)
        except Relationship.DoesNotExist:
            return Response({'error': 'Relationships not found'}, status=404)

    def put(self, request):
        user_id = int(request.data.get('user_id', 0))
        status = request.data.get('status', None)

        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status=404)

        if status:
            if status == 'block':
                from_user_rel = Relationship.objects.get(from_user=request.user, to_user=to_user)
                from_user_rel.status = RelationshipStatus.objects.get(name=status)
                from_user_rel.save()

                to_user_rel = Relationship.objects.get(from_user=request.user, to_user=to_user)
                to_user_rel.status = RelationshipStatus.objects.get(name='blocked')
                to_user_rel.save()
                return Response('Block', status=200)
            elif status == 'unblock':
                Relationship.objects.get(from_user=request.user, to_user=to_user).delete()
                Relationship.objects.get(from_user=to_user, to_user=request.user).delete()
                return Response('Unblock', status=200)

        to_user_query = Q(from_user=to_user) & Q(to_user=request.user)
        from_user_query = Q(from_user=request.user) & Q(to_user=to_user)

        try:
            relationship = Relationship.objects.get(to_user_query)
            if relationship.status.name == 'following':
                relationship.status = RelationshipStatus.objects.get(name='friend')
                relationship.save()

                relationship = Relationship.objects.get(from_user_query)
                relationship.status = RelationshipStatus.objects.get(name='friend')
                relationship.save()
                return Response('Success', status=200)
            elif relationship.status.name == 'block':
                return Response('User blocked you', status=403)
        except Relationship.DoesNotExist:
            try:
                relationship = Relationship.objects.get(from_user_query)
                if relationship.status.name == 'follow':
                    return Response('Duplicate', status=409)
            except Relationship.DoesNotExist:
                status = RelationshipStatus.objects.get(name='follow')
                Relationship.objects.create(from_user=to_user, to_user=request.user, status=status)
                return Response('created', status=200)


class UserAPIView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        kwargs = {'id': self.request.GET.get('user_id', self.request.user.id)}
        queryset = self.filter_queryset(self.queryset)
        return get_object_or_404(queryset, **kwargs)

    def get_query(self):
        search = self.request.GET.get('search', '')

        if search:
            return Q(Q(first_name__istartswith=search) | Q(
                last_name__istartswith=search) | Q(username__istartswith=search))
        return Q()

    def get_queryset(self):
        return self.queryset.filter(self.get_query()).exclude(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request.user.update(data=request.data)
        return Response('Updated', status=201)

    def update(self, request, *args, **kwargs):
        request.user.set_vk_info(data=request.data)
        return Response('Updated', status=201)
