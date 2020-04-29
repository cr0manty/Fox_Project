from django.contrib import admin

from .models import MyApp, AppVersions


@admin.register(MyApp)
class MyAppAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(AppVersions)
class AppVersionsAdmin(admin.ModelAdmin):
    readonly_fields = ('create_date', )
