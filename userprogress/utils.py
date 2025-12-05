from journey.models import PersonaJourney, Journey, Days
from userprogress.models import UserJourneyProgress


def get_current_day(user):
    if not user.category:
        return None, None, None

    progress = UserJourneyProgress.objects.filter(user=user).first()

    if not progress:
        persona = PersonaJourney.objects.get(persona=user.category)
        sequence = persona.sequence
        
        progress = UserJourneyProgress.objects.create(
            user=user,
            completed_days=0
        )

    # ---- GLOBAL DAY COUNT ---- #
    global_day = progress.completed_days + 1   # 1–56

    # ---- PERSONA SEQUENCE ---- #
    persona = PersonaJourney.objects.get(persona=user.category)
    sequence = persona.sequence               # [1,6,5,8,4,2,7,3]

    # ---- WHICH JOURNEY ---- #
    index = (global_day - 1) // 7             # 0–7
    if index >= len(sequence):
        return None, None, None

    journey_id = sequence[index]

    # ---- DAY ORDER ---- #
    order = (global_day - 1) % 7 + 1          # 1–7

    # ---- GET DAYS CONTENT ---- #
    day = Days.objects.filter(
        journey_id=journey_id,
        order=order
    ).first()

    return journey_id, (day.id if day else None), global_day
