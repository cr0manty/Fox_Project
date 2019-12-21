from django.contrib import admin

from .models import User, Proxy, UserLocation, FriendList


class UsersAdmin(admin.ModelAdmin):
    pass


class UserLocationAdmin(admin.ModelAdmin):
    pass


class FriendListAdmin(admin.ModelAdmin):
    pass


class ProxyAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UsersAdmin)
admin.site.register(UserLocation, UserLocationAdmin)
admin.site.register(FriendList, FriendListAdmin)
admin.site.register(Proxy, ProxyAdmin)
