from django.contrib import admin

from .models import User, Proxy, UserLocation, Relationship, RelationshipStatus


class UsersAdmin(admin.ModelAdmin):
    exclude = ('vk_password', 'vk_login',
               'is_active', 'last_login')


class UserLocationAdmin(admin.ModelAdmin):
    pass


class RelationshipAdmin(admin.ModelAdmin):
    pass


class RelationshipStatusAdmin(admin.ModelAdmin):
    pass


class ProxyAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UsersAdmin)
admin.site.register(UserLocation, UserLocationAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(RelationshipStatus, RelationshipStatusAdmin)
admin.site.register(Proxy, ProxyAdmin)
