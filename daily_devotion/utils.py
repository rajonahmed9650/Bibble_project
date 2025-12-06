# from journey.utils import get_today_journey_id
# from journey.models import Days


# def get_today_ids(user):
#     result = get_today_journey_id(user)

#     if not result:
#         return None , None , None
    
#     journey_id , day_number =result

#     day = Days.objects.filter(journey_id=journey_id).order_by("order").first()
#     if not day:
#         return journey_id,None,day_number
    
#     return journey_id,day.id , day_number
