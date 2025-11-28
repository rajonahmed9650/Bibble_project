from django.contrib import admin
from .models import DailyDevotion,DailyPrayer,MicroAction
# Register your models here.

admin.site.register(DailyDevotion)
admin.site.register(DailyPrayer)
admin.site.register(MicroAction)