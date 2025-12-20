from rest_framework.permissions import BasePermission
from payments.models import Subscription

class HasActiveSubscription(BasePermission):
    message = "Your subscription is inactive. Please buy a plan."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=user,
            is_active=True
        ).exists()
