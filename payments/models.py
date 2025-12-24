from django.db import models
from django.conf import settings


class Package(models.Model):
    PACKAGE_CHOICES = [
        ("free", "Free"),
        ("premium", "Premium"),
    ]

    package_name = models.CharField(
        max_length=10,
        choices=PACKAGE_CHOICES,
        default="free"
    )

    #  Correct money field
    monthly_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    yearly_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )
    weekly_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    # Correct Stripe Price ID fields
    stripe_monthly_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    stripe_yearly_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    stripe_weekly_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name


class Subscription(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("weekly","Weekly"),
        ("none", "None"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    package = models.ForeignKey(
        Package,
        on_delete=models.SET_NULL,  # better than CASCADE
        null=True,
        blank=True
    )

    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)

    current_plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="none"
    )
    expired_at = models.DateTimeField(null=True ,blank=True)


    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.current_plan}"
