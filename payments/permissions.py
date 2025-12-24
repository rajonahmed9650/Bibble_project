from django.utils import timezone
from rest_framework.permissions import BasePermission
from payments.models import Subscription

class HasActiveSubscription(BasePermission):
    message = "Your subscription has expired."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        sub = Subscription.objects.filter(user=user).first()
        if not sub:
            return False

        # 🔑 KEY CHECK
        if not sub.is_active:
            return False

        if sub.expired_at and sub.expired_at < timezone.now():
            # auto deactivate here
            sub.is_active = False
            sub.current_plan = "free"
            sub.save(update_fields=["is_active", "current_plan"])
            return False

        return True
