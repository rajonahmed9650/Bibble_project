from django.db import models
from django.utils import timezone
from django.conf import settings

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=200, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=200, null=True, blank=True)

    current_plan = models.CharField(max_length=20, choices=[
        ("trial", "Trial"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("none", "None"),
    ], default="none")

    trial_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


