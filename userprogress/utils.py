from .models import UserJourneyProgress, Days,UserDayProgress

def get_current_day(user):
    """
    Returns active journey_id, day_id and global day count.
    """

    progress = UserJourneyProgress.objects.filter(
        user=user,
        completed=False
    ).first()

    if not progress:
        return None, None, None

    journey_id = progress.journey_id
    completed_days = progress.completed_days
    next_day_number = (completed_days % 7) + 1

    day_obj = Days.objects.filter(journey_id=journey_id, order=next_day_number).first()

    if not day_obj:
        return journey_id, None, next_day_number

    return journey_id, day_obj.id, next_day_number

