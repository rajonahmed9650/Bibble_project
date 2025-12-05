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


class TodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        journey_id, day_id, global_day = get_current_day(user)

        if not day_id:
            return Response({"error": "No content available"}, status=400)

        devotion = DailyDevotion.objects.filter(day_id=day_id).first()
        prayer = DailyPrayer.objects.filter(day_id=day_id).first()
        action = MicroAction.objects.filter(day_id=day_id).first()
        quiz = DailyQuiz.objects.filter(days_id=day_id).first()

        return Response({
            "journey_id": journey_id,
            "global_day": global_day,
            "devotion": DailyDevotionSerializer(devotion).data if devotion else None,
            "prayer": DailyPrayerSerializer(prayer).data if prayer else None,
            "action": MicroActionSerializer(action).data if action else None,
            "quiz": DailyQuizSerializer(quiz).data if quiz else None
        })


class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Current state
        journey_id, day_id, global_day = get_current_day(user)

        if not day_id:
            return Response({"error": "No active day"}, status=400)

        # 1️Mark day complete
        UserDayProgress.objects.update_or_create(
            user=user,
            day_id_id=day_id,
            defaults={"completed": True}
        )

        # 2️Update journey progress
        progress = UserJourneyProgress.objects.filter(
            user=user,
            completed=False
        ).first()

        progress.completed_days += 1
        progress.save()

        # 3️Journey complete check
        journey_completed = (progress.completed_days % 7 == 0)
        next_journey_unlocked = False

        if journey_completed:
            persona = PersonaJourney.objects.get(persona=user.category)
            sequence = persona.sequence

            current_index = (progress.completed_days // 7) - 1

            # unlock next journey
            if current_index + 1 < len(sequence):
                next_journey_id = sequence[current_index + 1]
                next_journey = Journey.objects.get(id=next_journey_id)

                UserJourneyProgress.objects.get_or_create(
                    user=user,
                    journey=next_journey,
                    defaults={"completed_days": 0, "completed": False}
                )

                next_journey_unlocked = True

        # 4️RESPONSE
        return Response({
            "message": "🎉 Journey completed successfully!" if journey_completed else "Day completed",
            "global_day": global_day,
            "journey_completed": journey_completed,          # true / false
            "next_journey_unlocked": next_journey_unlocked  # true / false
        })


