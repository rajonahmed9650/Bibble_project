from datetime import date
from .models import PersonaJourney


def get_today_journey_id(user):

    if not user.category:
        return None
    
    try:
        persona_obj = PersonaJourney.objects.get(persona = user.category)
        sequence = persona_obj.sequence
    except PersonaJourney.DoesNotExist:
        return None

    if not user.journey_start_date:
        user.journey_start_date = date.today()
        user.save()

    days_passed = (date.today()-user.journey_start_date).days 

    index = days_passed % len(sequence)

    journey_id = sequence[index]
    day_number = days_passed + 1
    return journey_id,day_number          

