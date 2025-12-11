from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from userprogress.utils import get_current_day
from userprogress.models import UserDayProgress, UserJourneyProgress
from journey.models import PersonaJourney, Journey, Days

from daily_devotion.serializers import DailyDevotionSerializer, DailyPrayerSerializer, MicroActionSerializer
from daily_devotion.models import DailyDevotion, DailyPrayer, MicroAction

from quiz.models import DailyQuiz


# =======================
#   TODAY VIEW
# =======================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from userprogress.utils import get_current_day
from userprogress.models import UserJourneyProgress
from journey.models import PersonaJourney, Journey, Days

from daily_devotion.serializers import (
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer
)
from daily_devotion.models import DailyDevotion, DailyPrayer, MicroAction

from quiz.serializers import DailyQuizReadSerializer
from quiz.models import DailyQuiz
from payments.permissions import HasActiveSubscription

class TodayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get(self, request):
        user = request.user

        # 1) Must have category/persona
        if not user.category:
            return Response({"message": "No category found. Please finish assessment first."}, status=200)

        # 2) Get persona journey sequence
        persona = PersonaJourney.objects.filter(persona=user.category).first()
        if not persona:
            return Response({"message": "No persona configuration found."}, status=200)

        sequence = persona.sequence

        # 3) Find active journey (not completed)
        progress = UserJourneyProgress.objects.filter(user=user, completed=False).first()

        # If no progress → start with first journey
        if not progress:
            first_journey_id = sequence[0]
            progress = UserJourneyProgress.objects.create(
                user=user,
                journey_id=first_journey_id,
                completed_days=0,
                completed=False
            )

        # 4) Get current day from utility
        journey_id, day_id, global_day = get_current_day(user)

        if not day_id:
            return Response({
                "journey_id": journey_id,
                "global_day": global_day,
                "day": None,
                "devotion": None,
                "prayer": None,
                "action": None,
                "quiz": None,
                "message": "No content available for this day"
            }, status=200)

        # 5) Fetch Current day
        day = Days.objects.filter(id=day_id).first()

        # 6) Fetch All day-content
        devotion = DailyDevotion.objects.filter(day_id_id=day_id).first()
        prayer = DailyPrayer.objects.filter(day_id_id=day_id).first()
        action = MicroAction.objects.filter(day_id_id=day_id).first()
        quizzes = DailyQuiz.objects.filter(days_id=day_id)


        # Return everything in 1 API
        return Response({
            "category": user.category,
            "global_day": global_day,
            "journey": {
                "id": progress.journey.id,
                "name": progress.journey.name,
            },
            "day": {
                "id": day.id,
                "title": day.name,
                "order": day.order,
                "image": request.build_absolute_uri(day.image.url) if day.image else None
            },
            "global_day": global_day,
            "prayer": DailyPrayerSerializer(prayer,context = {"request":request}).data if prayer else None,
            "devotion": DailyDevotionSerializer(devotion).data if devotion else None,
            "action": MicroActionSerializer(action).data if action else None,
            "quiz": DailyQuizReadSerializer(quizzes,many=True).data if quizzes else None,
            "message": "Today's full content loaded successfully"
        }, status=200)



# ===========================================
#           COMPLETE DAY VIEW
# ===========================================

class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def post(self, request):
        user = request.user

        # 0️⃣ Validate POST body
        if request.data.get("day_completed") != True:
            return Response({"error": "day_completed=true is required"}, status=400)

        # 1️⃣ Get current journey + day
        journey_id, day_id, global_day = get_current_day(user)

        if not day_id:
            return Response({"error": "No active day"}, status=400)

        current_day = Days.objects.get(id=day_id)
        current_order = current_day.order

        # 2️⃣ Mark day completed (user wise)
        UserDayProgress.objects.update_or_create(
            user=user,
            day_id_id=day_id,
            defaults={"completed": True}
        )

        # 3️⃣ Update journey progress
        progress, _ = UserJourneyProgress.objects.get_or_create(
            user=user,
            journey_id=journey_id,
            defaults={"completed_days": 0, "completed": False}
        )

        progress.completed_days += 1
        progress.save()

        # 4️⃣ Check if next day exists in same journey
        next_day = Days.objects.filter(
            journey_id=journey_id,
            order=current_order + 1
        ).first()

        if next_day:
            return Response({
                "message": "Day completed → next day unlocked!",
                "day_title": current_day.name,
                "next_day": {
                    "id": next_day.id,
                    "title": next_day.name,
                    "order": next_day.order,
                    "journey_id": journey_id
                }
            }, status=200)

        # --------------------------
        # 5️⃣ No more days → JOURNEY COMPLETED
        # --------------------------

        progress.completed = True
        progress.save()

        persona = PersonaJourney.objects.get(persona=user.category)
        sequence = persona.sequence              # e.g. [1,6,5,8,4,2,7,3]

        current_index = sequence.index(journey_id)
        last_index = len(sequence) - 1

        # --------------------------
        # 6️⃣ CASE A — More journeys remaining
        # --------------------------
        if current_index < last_index:
            next_journey_id = sequence[current_index + 1]

        else:
            # --------------------------
            # 7️⃣ CASE B — All journeys done → FULL RESET
            # --------------------------
            UserJourneyProgress.objects.filter(user=user).delete()
            UserDayProgress.objects.filter(user=user).delete()

            next_journey_id = sequence[0]   # restart from first journey

        # --------------------------
        # 8️⃣ Create progress for next journey (NO DUPLICATE ERROR)
        # --------------------------
        next_progress = UserJourneyProgress.objects.filter(
            user=user,
            journey_id=next_journey_id
        ).first()

        if not next_progress:
            next_progress = UserJourneyProgress.objects.create(
                user=user,
                journey_id=next_journey_id,
                completed_days=0,
                completed=False
            )
        else:
            # Reset if exists
            next_progress.completed_days = 0
            next_progress.completed = False
            next_progress.save()

        # --------------------------
        # 9️⃣ Return final response
        # --------------------------
        next_journey = Journey.objects.get(id=next_journey_id)

        return Response({
            "message": "🎉 Journey completed! Next journey unlocked.",
            "completed_journey": current_day.journey_id.name,
            "next_journey": {
                "id": next_journey.id,
                "name": next_journey.name
            }
        }, status=200)
