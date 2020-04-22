from django.db import models
from django.urls import reverse
from django.utils import timezone

from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField


class MyApp(models.Model):
    title = models.CharField('Title', max_length=255)
    slug = models.SlugField()
    ios_app = FilerFileField(related_name='ios', on_delete=models.CASCADE, blank=True, null=True)
    android_app = FilerFileField(related_name='android', on_delete=models.CASCADE, blank=True, null=True)
    icon = FilerImageField(related_name='app_icon', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=10, help_text='0.0.1')
    details = models.TextField(default='Your version is out of date, please upgrade to a new version.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated_at = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse('', kwargs={'slug': self.slug})

    def __str__(self):
        return '{} - {}'.format(self.title, self.version)
