from django.contrib import admin
from .models import UserJourneyProgress,UserDayProgress,UserDayItemProgress,jourenystepitem
# Register your models here.


admin.site.register(UserJourneyProgress)

class UserDayProgressAdmin(admin.ModelAdmin):
    list_display = ("id","user")
    ordering = ("id",)

admin.site.register(UserDayProgress,UserDayProgressAdmin)
class UseryDayItemprogressAdmin(admin.ModelAdmin):
    list_display = ("user","day","completed")

admin.site.register(UserDayItemProgress,UseryDayItemprogressAdmin)

class JourneySetpItem(admin.ModelAdmin):
    list_display = ("journey_id","days_id","is_completed")

admin.site.register(jourenystepitem,JourneySetpItem)