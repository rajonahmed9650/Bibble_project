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

    monthly_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    weekly_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    stripe_monthly_price_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_yearly_price_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_weekly_price_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name


class Subscription(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("none", "None"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)

    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(
        max_length=255, null=True, blank=True
    )

    current_plan = models.CharField(
        max_length=20, choices=PLAN_CHOICES, default="none"
    )
    expired_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.current_plan}"


class SubscriptionInvoice(models.Model):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="invoices"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)

    plan = models.CharField(max_length=20)

    transaction_id = models.CharField(max_length=255, unique=True)
    stripe_invoice_id = models.CharField(max_length=255, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    payment_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.plan} - {self.amount}"





# # subscriptions/models.py
# from django.conf import settings
# from django.db import models

# class MobileSubscription(models.Model):
#     PLATFORM_CHOICES = (
#         ("ios", "iOS"),
#         ("android", "Android"),
#     )

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)

#     product_id = models.CharField(max_length=100)
#     transaction_id = models.CharField(max_length=200, unique=True)

#     is_trial = models.BooleanField(default=False)
#     expires_at = models.DateTimeField()
#     is_active = models.BooleanField(default=False)

#     raw_response = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user} | {self.product_id}"
