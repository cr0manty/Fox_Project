from django.contrib import admin
from authtools.admin import UserAdmin

from .models import User, Relationship, RelationshipStatus
from .forms import StaffChangeForm

fieldsets = UserAdmin.fieldsets


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets += (
        ('User data', {'fields': (
            'first_name', 'last_name'
        )}),
        ('VK Data', {'fields': (
            'user_id', 'vk_login', 'can_use_vk', 'vk_password'
        )}),
        ('Image', {'fields': (
            'image',
        )}),
    )
    form = StaffChangeForm


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    pass


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    pass
