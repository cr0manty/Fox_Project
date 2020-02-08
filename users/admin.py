from django.contrib import admin

from .models import User, Proxy, Relationship, RelationshipStatus


class UsersAdmin(admin.ModelAdmin):
    exclude = ('vk_password', 'is_active', 'last_login')


class RelationshipAdmin(admin.ModelAdmin):
    pass


class RelationshipStatusAdmin(admin.ModelAdmin):
    pass


class ProxyAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UsersAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(RelationshipStatus, RelationshipStatusAdmin)
admin.site.register(Proxy, ProxyAdmin)
