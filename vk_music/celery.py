import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vk_music.settings.local')

app = Celery('vk_music')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
