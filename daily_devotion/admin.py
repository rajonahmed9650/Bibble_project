from django.contrib import admin
from .models import DailyDevotion,DailyPrayer,MicroAction,DailyReflectionSpace
# Register your models here.
class DailyDevotionAdmin(admin.ModelAdmin):
    list_display = ("id","scripture_name",)
    ordering =("id",)

class DailyPrayerAdmin(admin.ModelAdmin):
    list_display = ("id","prayer")
    ordering = ("id",)    

admin.site.register(DailyDevotion,DailyDevotionAdmin)

admin.site.register(DailyPrayer,DailyPrayerAdmin)

class MicroActionAdmin(admin.ModelAdmin):
    list_display = ("id","action")
    ordering =("id",)

admin.site.register(MicroAction,MicroActionAdmin)
admin.site.register(DailyReflectionSpace)