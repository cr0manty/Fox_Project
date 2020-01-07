from django.contrib import admin

from .models import Log


class LogAdmin(admin.ModelAdmin):
    pass


admin.site.register(Log, LogAdmin)
