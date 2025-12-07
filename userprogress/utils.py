from journey.models import PersonaJourney, Journey, Days
from userprogress.models import UserJourneyProgress

def get_current_day(user):

    # ----- 1) USER CATEGORY CHECK -----
    if not user.category:
        return None, None, None

    # ----- 2) INITIAL USER PROGRESS -----
    progress = UserJourneyProgress.objects.filter(user=user).first()

    # New user: no progress exists
    if not progress:

        # SAFE persona lookup
        persona = PersonaJourney.objects.filter(persona=user.category).first()
        if not persona:
            # No persona config in DB yet
            return None, None, None

        # Create progress safely
        progress = UserJourneyProgress.objects.create(
            user=user,
            completed_days=0,
            journey_id=None,   # optional, depends on your model
            completed=False
        )

    # ----- 3) GLOBAL DAY -----
    global_day = progress.completed_days + 1  # 1–56

    # ----- 4) PERSONA SAFE CHECK AGAIN -----
    persona = PersonaJourney.objects.filter(persona=user.category).first()
    if not persona:
        return None, None, None

    sequence = persona.sequence  # example: [1,6,5,8,4,2,7,3]

    # ----- 5) WHICH JOURNEY -----
    index = (global_day - 1) // 7
    if index >= len(sequence):
        return None, None, None

    journey_id = sequence[index]

    # ----- 6) WHICH DAY -----
    order = (global_day - 1) % 7 + 1  # 1–7

    # ----- 7) GET DAY OBJECT -----
    day = Days.objects.filter(
        journey_id=journey_id,
        order=order
    ).first()

    return journey_id, (day.id if day else None), global_day
