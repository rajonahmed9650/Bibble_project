from django.contrib import admin
from .models import UserJourneyProgress,UserDayProgress,UserDayItemProgress,jourenystepitem
# Register your models here.


admin.site.register(UserJourneyProgress)

class UserDayProgressAdmin(admin.ModelAdmin):
    list_display = ("id","user")
    ordering = ("id",)

admin.site.register(UserDayProgress,UserDayProgressAdmin)

admin.site.register(UserDayItemProgress)
admin.site.register(jourenystepitem)