# notifications/helpers.py

from userprogress.models import UserDayItemProgress

ITEM_SEQUENCE = ["prayer", "devotion", "quiz", "action", "reflection"]

def get_current_stage(user, day):
    items = UserDayItemProgress.objects.filter(user=user, day=day)
    completed = {i.item_type: i.completed for i in items}

    for stage in ITEM_SEQUENCE:
        if not completed.get(stage, False):
            return stage

    return None
