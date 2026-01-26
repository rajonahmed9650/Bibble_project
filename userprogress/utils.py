from django.utils import timezone
from datetime import timedelta
from userprogress.models import UserDayProgress

DAY_UNLOCK_DELAY = timedelta(days=1)  

def get_current_day(user, journey):
    
    current_dp = UserDayProgress.objects.filter(
        user=user,
        day_id__journey_id=journey,
        status="current"
    ).select_related("day_id").first()

    if current_dp:
        return current_dp.day_id

    last_completed = UserDayProgress.objects.filter(
        user=user,
        day_id__journey_id=journey,
        status="completed"
    ).order_by("-completed_at").first()

    if not last_completed:
        return None

    if last_completed.completed_at <= timezone.now() - DAY_UNLOCK_DELAY:
        next_locked = UserDayProgress.objects.filter(
            user=user,
            day_id__journey_id=journey,
            status="locked"
        ).order_by("day_id__order").select_related("day_id").first()

        if next_locked:
            next_locked.status = "current"
            next_locked.save()
            return next_locked.day_id

    # ✅ important line
    return last_completed.day_id
