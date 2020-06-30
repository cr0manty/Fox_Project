from django.db import models
from django.utils import timezone

from filer.fields.image import FilerImageField
from ckeditor.fields import RichTextField


class MyApp(models.Model):
    title = models.CharField('Title', max_length=255)
    slug = models.SlugField()

    icon = FilerImageField(related_name='app_icon', on_delete=models.CASCADE)
    description = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated_at = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def last_version(self):
        try:
            return self.versions.latest('id')
        except AppVersions.DoesNotExist:
            return

    @property
    def version_amount(self):
        return self.versions.count()

    @property
    def short_description(self):
        return self.description[:60]

    def __str__(self):
        return self.title


class AppVersions(models.Model):
    version = models.CharField(max_length=10, help_text='x.x.x')
    details = RichTextField(default='Bug fixes')
    update_details = models.TextField(default='Your version is out of date, please upgrade to a new version.')
    app = models.ForeignKey(MyApp, on_delete=models.CASCADE, related_name='versions')
    create_date = models.DateTimeField(auto_now_add=True)
    web_version = models.URLField(blank=True, null=True)
    ios_app = models.URLField(blank=True, null=True)
    android_app = models.URLField(blank=True, null=True)

    @property
    def type_amount(self):
        return (self.web_version is not None) + (self.android_app is not None) + (self.ios_app is not None)

    def __str__(self):
        return '{} - {}'.format(self.version, self.app.title)
