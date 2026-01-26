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

      
        if not current_dp.completed_at:
            return current_dp.day_id

        if timezone.now() - current_dp.completed_at < DAY_UNLOCK_DELAY:
            return current_dp.day_id

   
        current_dp.status = "completed"
        current_dp.save()

 
        next_locked = UserDayProgress.objects.filter(
            user=user,
            day_id__journey_id=journey,
            status="locked"
        ).order_by("day_id__order").select_related("day_id").first()

        if next_locked:
            next_locked.status = "current"
            next_locked.save()
            return next_locked.day_id

        return None

    
    return None
