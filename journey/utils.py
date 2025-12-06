# from datetime import date,datetime,timedelta
# from .models import PersonaJourney


# def get_today_journey_id(user):

#     if not user.category:
#         return None
    
#     try:
#         persona_obj = PersonaJourney.objects.get(persona = user.category)
#         sequence = persona_obj.sequence
#     except PersonaJourney.DoesNotExist:
#         return None

#     if not user.journey_start_date:
#         user.journey_start_date = date.today()
#         user.save()

#     start_datetime = datetime.combine(user.journey_start_date, datetime.min.time())
#     days_passed = int((datetime.now() - start_datetime).total_seconds() // 60) 

#     index = days_passed % len(sequence)

#     journey_id = sequence[index]
#     day_number = days_passed + 1
#     return journey_id,day_number          

