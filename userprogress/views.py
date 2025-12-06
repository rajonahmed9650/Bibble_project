from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from userprogress.utils import get_current_day
from userprogress.models import UserDayProgress, UserJourneyProgress
from journey.models import PersonaJourney, Journey, Days

from daily_devotion.serializers import DailyDevotionSerializer, DailyPrayerSerializer, MicroActionSerializer
from daily_devotion.models import DailyDevotion, DailyPrayer, MicroAction
from quiz.serializers import DailyQuizSerializer
from quiz.models import DailyQuiz


# =======================
#   TODAY VIEW
# =======================
class TodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        journey_id, day_id, global_day = get_current_day(user)

        if not day_id:
            return Response({
                "journey_id": journey_id,
                "global_day": global_day,
                "devotion": None,
                "prayer": None,
                "action": None,
                "quiz": None,
                "message": "No content available for this day"
            }, status=200)  # ⬅️ IMPORTANT

        devotion = DailyDevotion.objects.filter(day_id_id=day_id).first()
        prayer = DailyPrayer.objects.filter(day_id_id=day_id).first()
        action = MicroAction.objects.filter(day_id_id=day_id).first()
        quiz = DailyQuiz.objects.filter(days_id_id=day_id).first()  # ⬅️ FIXED

        return Response({
            "journey_id": journey_id,
            "global_day": global_day,
            "devotion": DailyDevotionSerializer(devotion).data if devotion else None,
            "prayer": DailyPrayerSerializer(prayer).data if prayer else None,
            "action": MicroActionSerializer(action).data if action else None,
            "quiz": DailyQuizSerializer(quiz).data if quiz else None
        })


# =======================
#   COMPLETE DAY
# =======================



class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Current state
        journey_id, day_id, global_day = get_current_day(user)

        if not day_id:
            return Response({"error": "No active day"}, status=400)

        # get current day title
        day_obj = Days.objects.get(id=day_id)
        day_title = day_obj.name

        # Mark day complete
        UserDayProgress.objects.update_or_create(
            user=user,
            day_id_id=day_id,
            defaults={"completed": True}
        )

        # 2️Update USER journey progress
        progress = UserJourneyProgress.objects.get(
            user=user,
            journey_id=journey_id
        )

        progress.completed_days += 1

        #  journey complete check
        journey_completed = (progress.completed_days % 7 == 0)

        if journey_completed:
            progress.completed = True

        progress.save()

        #  next journey unlock
        next_journey_unlocked = False
        next_journey_name = None

        if journey_completed:
            persona = PersonaJourney.objects.get(persona=user.category)
            sequence = persona.sequence

            # find index in sequence
            current_index = (progress.completed_days // 7) - 1

            if current_index + 1 < len(sequence):
                next_journey_id = sequence[current_index + 1]
                next_journey = Journey.objects.get(id=next_journey_id)

                # create progress if not exists
                UserJourneyProgress.objects.get_or_create(
                    user=user,
                    journey_id=next_journey,
                    defaults={"completed_days": 0, "completed": False}
                )

                next_journey_unlocked = True
                next_journey_name = next_journey.name

        # Response
        return Response({
            "message": "🎉 Journey completed successfully!" if journey_completed else "Day completed",
            "global_day": global_day,
            "day_title": day_title,                
            "journey_completed": journey_completed,
            "next_journey_unlocked": next_journey_unlocked,
            "next_journey_name": next_journey_name  
        })



