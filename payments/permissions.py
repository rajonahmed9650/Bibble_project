from django.utils import timezone
from rest_framework.permissions import BasePermission
from payments.models import Subscription


class HasActiveSubscription(BasePermission):
    message = "Your subscription has expired."

    def has_permission(self, request, view):
        user = request.user
        now = timezone.now()

        if not user or not user.is_authenticated:
            return False

        
        active_sub = Subscription.objects.filter(
            user=user,
            is_active=True
        ).order_by("expired_at").first()

      
        if active_sub and active_sub.expired_at and active_sub.expired_at < now:
            active_sub.is_active = False
            active_sub.save(update_fields=["is_active"])

            active_sub = None  
        if not active_sub:
            next_sub = Subscription.objects.filter(
                user=user,
                expired_at__gt=now,
                is_active=False
            ).order_by("expired_at").first()

            if next_sub:
                next_sub.is_active = True
                next_sub.save(update_fields=["is_active"])
                return True

      
            return False

      
        return True
