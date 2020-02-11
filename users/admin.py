from django.contrib import admin
from authtools.admin import UserAdmin

from .models import User, Relationship, RelationshipStatus
from .forms import StaffChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = StaffChangeForm


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    pass


@admin.register(RelationshipStatus)
class RelationshipStatusAdmin(admin.ModelAdmin):
    pass
