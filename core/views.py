from django.db.models import Q
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class AmountModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_filter_query(self):
        return Q()

    def filter(self, queryset):
        return queryset.filter(self.get_filter_query())

    def list(self, request, *args, **kwargs):
        queryset = self.filter(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'amount': queryset.count(),
            'result': serializer.data
        })
