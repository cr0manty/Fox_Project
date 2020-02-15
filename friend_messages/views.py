from django.db.models import Q
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from friend_messages.serializers import MessageSerializer
from friend_messages.models import Message


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = MessageSerializer
    queryset = Message.objects.filter(deleted=False)

    def filter_queryset(self, queryset):
        query = Q(from_user=self.request.user) & Q(to_user__id=self.kwargs.get('user_id'))
        return queryset.filter(query)
