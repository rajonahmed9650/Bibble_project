from datetime import timedelta
from django.utils import timezone
from .models import Subscription

PLAN_DAYS = {
    "free": 7,
    "weekly": 7,
    "monthly": 30,
    "yearly": 365,
}

def schedule_subscription(user, plan):
    """
    Decide when a subscription should start.
    - If previous subscription still active → queue
    - Else → start now
    """
    now = timezone.now()
    days = PLAN_DAYS[plan]

    last_sub = (
        Subscription.objects
        .filter(user=user)
        .order_by("-expired_at")
        .first()
    )

    if last_sub and last_sub.expired_at and last_sub.expired_at > now:
        start_time = last_sub.expired_at
        is_active = False
    else:
        start_time = now
        is_active = True

    end_time = start_time + timedelta(days=days)
    return start_time, end_time, is_active
