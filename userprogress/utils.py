# userprogress/utils.py
from .models import UserDayProgress

def get_current_day(user, journey):
    dp = UserDayProgress.objects.filter(
        user=user,
        status="current",
        day_id__journey_id=journey
    ).select_related("day_id").first()

    return dp.day_id if dp else None
