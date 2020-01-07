from django.db import models


class Log(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    exception = models.TextField(blank=True, null=True)
    additional_text = models.TextField(blank=True, null=True)
