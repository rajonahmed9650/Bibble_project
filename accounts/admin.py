from django.contrib import admin
from .models import User,Profile,Social_login,Sessions
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone',)
    ordering = ('id',)
admin.site.register(User, UserAdmin)

admin.site.register(Sessions)
admin.site.register(Profile)
admin.site.register(Social_login)