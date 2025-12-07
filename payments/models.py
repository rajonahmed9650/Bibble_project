# payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Subscription(models.Model):
    PLAN_CHOICES = [
        ("trial", "Trial"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("none", "None"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=200, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=200, null=True, blank=True)

    current_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="none")

    # Trial expiry
    trial_end = models.DateTimeField(null=True, blank=True)

    # Paid plan expiry (Stripe billing period end)
    billing_period_end = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check subscription expired status"""
        if self.billing_period_end and self.billing_period_end < timezone.now():
            return True
        return False

    def __str__(self):
        return f"{self.user} - {self.current_plan} ({'active' if self.is_active else 'inactive'})"
