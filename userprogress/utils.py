from userprogress.models import UserDayProgress

def get_current_day(user, journey):
    """
    READ ONLY:

    """
    dp = UserDayProgress.objects.filter(
        user=user,
        day_id__journey_id=journey,
        status="current"
    ).select_related("day_id").first()

    return dp.day_id if dp else None
