from django.contrib import admin

from .models import MyApp, AppVersions


@admin.register(MyApp)
class MyAppAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(AppVersions)
