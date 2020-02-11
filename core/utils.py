from django.db.models import Q
from rest_framework.permissions import BasePermission

from vk_api import VkApi, audio

from users.models import Relationship


def get_vk_auth(user):
    login = user.username
    vk_session = VkApi(login=login, password=user.vk_password, config_filename='config.json')
    vk_session.auth()
    vk_session.get_api()
    return vk_session


def get_vk_songs(vk_session, user_id=None):
    vk_audio = audio.VkAudio(vk_session)
    return vk_audio.get(owner_id=user_id) if user_id else vk_audio.get()


def get_vk_user_data(vk_session):
    return vk_session.method('users.get')[0]


class IsFriend(BasePermission):
    def has_permission(self, request, view):
        query = Q(Q(from_user=request.user) | Q(to_user=request.user)) & Q(status__code=1)
        try:
            Relationship.objects.get(query)
            return True
        except Relationship.DoesNotExist:
            return False
