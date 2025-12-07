from rest_framework.permissions import BasePermission
from django.utils import timezone
from payments.models import Subscription

class HasActiveSubscription(BasePermission):

    message = "Your subscription is inactive. Please buy a plan."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        sub = Subscription.objects.filter(user=request.user).first()
        now = timezone.now()

        # Trial active
        if sub and sub.current_plan == "trial" and sub.trial_end and sub.trial_end > now:
            return True

        # Paid active
        if sub and sub.current_plan in ["monthly","yearly"] and sub.billing_period_end and sub.billing_period_end > now:
            return True

        return False
