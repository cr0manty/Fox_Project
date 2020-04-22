from django.contrib import admin

from .models import MyApp


@admin.register(MyApp)
class MyAppAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
