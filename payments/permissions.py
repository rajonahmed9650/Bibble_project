from rest_framework.permissions import BasePermission
from django.utils import timezone
from payments.models import Subscription
from .utils import deactivate_expired_subscriptions

class HasActiveSubscription(BasePermission):

    message = "Your subscription is inactive. Please buy a plan."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        deactivate_expired_subscriptions()
        
        sub = Subscription.objects.filter(user=request.user).first()

        if not sub:
            self.message = "No subscription found."
            return False

        now = timezone.now()

        # FREE trial (7 days)
        if sub.current_plan == "free":
            if sub.expired_at and sub.expired_at > now:
                return True
            self.message = "Free trial expired. Buy premium."
            return False

        # PREMIUM plan
        if sub.current_plan in ["monthly", "yearly"]:
            if sub.expired_at and sub.expired_at > now:
                return True
            self.message = "Premium expired. Renew subscription."
            return False

        return False
