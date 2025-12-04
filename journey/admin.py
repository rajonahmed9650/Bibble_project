from django.contrib import admin
from .models import Journey,Journey_icon,JourneyDetails,Days,PersonaJourney
# Register your models here.


admin.site.register(Journey)
admin.site.register(Journey_icon)
admin.site.register(JourneyDetails)

class DaysAdmin(admin.ModelAdmin):
    list_display = ("id","name",)
    ordering =("id",)
admin.site.register(Days,DaysAdmin)
class PersonJourneyAdmin(admin.ModelAdmin):
    list_display = ("id","persona",)
    ordering = ("id",)
admin.site.register(PersonaJourney,PersonJourneyAdmin)