

# =======================
#   TODAY VIEW
# =======================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .utils import get_current_day
from .models import UserDayProgress,UserJourneyProgress
from journey.models import PersonaJourney, Journey, Days,JourneyDetails
from journey.serializers import JourneyDetailsSerializer

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

        # 3) Find active journey
        progress = UserJourneyProgress.objects.filter(user=user, completed=False).first()
        if not progress:
            progress = UserJourneyProgress.objects.create(
                user=user,
                journey_id=sequence[0],
                completed_days=0,
                completed=False
            )

        # 4) Get current day
        journey_id, day_id, global_day = get_current_day(user)
        if not day_id:
            return Response({"message": "No content available"}, status=200)

        # 5) Fetch data
        day = Days.objects.filter(id=day_id).first()
        details = JourneyDetails.objects.filter(journey_id=progress.journey.id)

        devotion = DailyDevotion.objects.filter(day_id_id=day_id).first()
        prayer = DailyPrayer.objects.filter(day_id_id=day_id).first()
        action = MicroAction.objects.filter(day_id_id=day_id).first()
        quizzes = DailyQuiz.objects.filter(days_id=day_id)

        return Response({
            "category": user.category,
            "global_day": global_day,
            "journey": {
                "id": progress.journey.id,
                "name": progress.journey.name,
                "details": JourneyDetailsSerializer(details, many=True, context={"request": request}).data
            },
            "day": {
                "id": day.id,
                "title": day.name,
                "order": day.order,
                "image": request.build_absolute_uri(day.image.url) if day.image else None
            },
            "prayer": DailyPrayerSerializer(prayer, context={"request": request}).data if prayer else None,
            "devotion": DailyDevotionSerializer(devotion).data if devotion else None,
            "action": MicroActionSerializer(action).data if action else None,
            "quiz": DailyQuizReadSerializer(quizzes, many=True).data if quizzes else None,
            "message": "Today's full content loaded successfully"
        }, status=200)


class UserProgressDaysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1️⃣ User active journey progress
        journey_progress = UserJourneyProgress.objects.filter(
            user=user,
            completed=False
        ).first()

        if not journey_progress:
            return Response({
                "message": "No active journey found"
            }, status=200)

        journey = journey_progress.journey

        # 2️⃣ All days of this journey (order wise)
        days = Days.objects.filter(
            journey_id=journey
        ).order_by("order")

        # 3️⃣ Completed day ids for this user & journey
        completed_day_ids = set(
            UserDayProgress.objects.filter(
                user=user,
                completed=True,
                day_id__journey_id=journey
            ).values_list("day_id_id", flat=True)
        )

        result = []

        for day in days:
            if day.id in completed_day_ids:
                status = "completed"
            elif day.order == len(completed_day_ids) + 1:
                status = "current"
            else:
                status = "locked"

            result.append({
                "day_id": day.id,
                "day_name": day.name,
                "day_order": day.order,
                "status": status
            })

        return Response({
            "journey": {
                "id": journey.id,
                "name": journey.name
            },
            "days": result
        })



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
