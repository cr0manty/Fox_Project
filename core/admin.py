from django.contrib import admin

from .models import Log, RQLog


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    pass


@admin.register(RQLog)
class RQLogAdmin(admin.ModelAdmin):
    pass
