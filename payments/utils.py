# payments/utils.py

from django.utils import timezone
from datetime import timedelta
from .models import Subscription

from accounts.utils.messages import SYSTEM_MESSAGES

# def set_premium_expire(user, plan):
#     sub = Subscription.objects.get(user=user)

#     now = timezone.now()

#     if plan == "monthly":
#         sub.expired_at = now + timedelta(days=30)

#     elif plan == "yearly":
#         sub.expired_at = now + timedelta(days=365)

#     sub.current_plan = plan
#     sub.is_active = True
#     sub.save()

#     return sub

def deactivate_expired_subscriptions():
    subs = Subscription.objects.filter(is_active=True)

    for sub in subs:
        # expired if date passed
        if sub.expired_at and sub.expired_at < timezone.now():
            sub.is_active = False
            sub.current_plan = "free"
            sub.save()

          
