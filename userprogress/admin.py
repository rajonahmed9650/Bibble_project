from django.contrib import admin
from .models import UserJourneyProgress,UserDayProgress
# Register your models here.


admin.site.register(UserJourneyProgress)
admin.site.register(UserDayProgress)