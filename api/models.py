from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q

from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission

from users.models import Relationship


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class IsFriend(BasePermission):
    def has_permission(self, request, view):
        query = Q(Q(from_user=request.user) | Q(to_user=request.user)) & Q(status__code=1)
        try:
            Relationship.objects.get(query)
            return True
        except Relationship.DoesNotExist:
            return False
