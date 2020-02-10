from django.contrib import admin
from authtools.admin import UserAdmin

from .models import User
from .forms import StaffChangeForm


class CustomUserAdmin(UserAdmin):
    form = StaffChangeForm


admin.site.register(User, CustomUserAdmin)
