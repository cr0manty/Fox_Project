from django.contrib import admin
from authtools.admin import UserAdmin

from .models import User, Relationship, RelationshipStatus
from .forms import StaffChangeForm

fieldsets = UserAdmin.fieldsets


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('is_active', 'username', 'is_staff', 'is_superuser', 'can_use_vk', 'date_joined')
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
