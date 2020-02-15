from django.db import models

from users.models import User


class Message(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user_message')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user_message')
    send_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    silence = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
