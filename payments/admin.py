from django.contrib import admin
from .models import Subscription,Package
# Register your models here.
admin.site.register(Subscription)

class PackageAdmin(admin.ModelAdmin):
    list_display = ("id","package_name","monthly_price","yearly_price")

    ordering = ("id",)


admin.site.register(Package,PackageAdmin)