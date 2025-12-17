from journey.models import Days
from userprogress.models import UserDayProgress


def get_current_day(user, journey):
    # 1️⃣ explicitly current day
    dp = UserDayProgress.objects.filter(
        user=user,
        day_id__journey_id=journey,
        status="current"
    ).select_related("day_id").first()

    if dp:
        return dp.day_id

    # 2️⃣ fallback using completed_days
    completed_count = UserDayProgress.objects.filter(
        user=user,
        day_id__journey_id=journey,
        status="completed"
    ).count()

    next_order = completed_count + 1

    return Days.objects.filter(
        journey_id=journey,
        order=next_order
    ).first()
