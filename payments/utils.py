from django.utils import timezone
from payments.models import Subscription, Package

class SubscriptionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # শুধু logged-in user এর জন্য
        if user.is_authenticated:
            sub = Subscription.objects.filter(
                user=user,
                is_active=True
            ).first()

            if (
                sub and
                sub.expired_at and
                sub.expired_at < timezone.now()
            ):
                # EXPIRED → AUTO DEACTIVATE
                free_pkg = Package.objects.filter(package_name="free").first()

                sub.is_active = False
                sub.current_plan = "free"
                sub.package = free_pkg
                sub.save(update_fields=["is_active", "current_plan", "package"])

        return self.get_response(request)
