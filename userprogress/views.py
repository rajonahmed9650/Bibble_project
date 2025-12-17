
# progress/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.permissions import HasActiveSubscription
from journey.models import PersonaJourney, Days
from userprogress.models import UserJourneyProgress, UserDayProgress

from daily_devotion.models import DailyDevotion, DailyPrayer, MicroAction
from daily_devotion.serializers import (
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer
)
from quiz.models import DailyQuiz
from quiz.serializers import DailyQuizReadSerializer
from userprogress.models import UserDayItemProgress

class TodayStepView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get(self, request, step):
        user = request.user

        persona = PersonaJourney.objects.filter(persona=user.category).first()
        sequence = persona.sequence

        # current journey
        progress = UserJourneyProgress.objects.filter(
            user=user, status="current"
        ).first()

        if not progress:
            progress = UserJourneyProgress.objects.create(
                user=user,
                journey_id=sequence[0],
                status="current"
            )

        # current day
        current_dp = UserDayProgress.objects.filter(
            user=user,
            day_id__journey_id=progress.journey,
            status="current"
        ).select_related("day_id").first()

        if not current_dp:
            first_day = Days.objects.filter(
                journey_id=progress.journey,
                order=1
            ).first()

            current_dp = UserDayProgress.objects.create(
                user=user,
                day_id=first_day,
                status="current"
            )

        day = current_dp.day_id


        # ✅ ADD HERE – load step progress (DO NOT REMOVE ANYTHING)
        step_progress = UserDayItemProgress.objects.filter(
            user=user,
            day=day,
            item_type=step
        ).first()


        # -----------------------------
        # STEP BASED RESPONSE
        # -----------------------------
        if step == "prayer":
            obj = DailyPrayer.objects.filter(day_id=day).first()
            data = DailyPrayerSerializer(obj, context={"request": request}).data if obj else None

        elif step == "devotion":
            obj = DailyDevotion.objects.filter(day_id=day).first()
            data = DailyDevotionSerializer(obj, context={"request": request}).data if obj else None

        elif step == "action":
            obj = MicroAction.objects.filter(day_id=day).first()
            data = MicroActionSerializer(obj, context={"request": request}).data if obj else None

        elif step == "quiz":
            quizzes = DailyQuiz.objects.filter(days_id=day)
            data = DailyQuizReadSerializer(quizzes, many=True).data

        else:
            return Response({"error": "Invalid step"}, status=400)

        return Response({
            "journey": {
                "id": progress.journey.id,
                "name": progress.journey.name,
                "status": progress.status
            },
            "day": {
                "id": day.id,
                "order": day.order,
                "title": day.name,
                "status": current_dp.status
            },
            "is_completed": step_progress.completed if step_progress else False,
            "data": data
        }, status=200)


class UserProgressDaysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, journey_id):
        user = request.user
        if not Days.objects.filter(journey_id=journey_id).exists():
            return Response(
                {"error": "Journey not found or has no days"},
                status=404
            )

        days = Days.objects.filter(
            journey_id=journey_id
        ).order_by("order")

        dp_map = {
            dp.day_id_id: dp.status
            for dp in UserDayProgress.objects.filter(
                user=user,
                day_id__journey_id=journey_id
            )
        }
        

        result = []
        for day in days:
            result.append({
                "day_id": day.id,
                "day_name": day.name,
                "order": day.order,
                "status": dp_map.get(day.id, "locked")
            })

        return Response({"days": result})





from django.db import transaction
from django.utils import timezone



from journey.models import Days, Journey, PersonaJourney


class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    @transaction.atomic
    def post(self, request):
        user = request.user
        today = timezone.now().date()

        # =====================================================
        # ❌ Rule: One calendar day → one day completion
        # =====================================================
        if UserDayProgress.objects.filter(
            user=user,
            completed_at=today
        ).exists():
            return Response(
                {"error": "Only one day can be completed per day"},
                status=400
            )

        # =====================================================
        # ✅ SERVER decides CURRENT DAY
        # =====================================================
        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current"
        ).select_related("day_id", "day_id__journey_id").first()

        if not current_dp:
            return Response(
                {"error": "No active day found"},
                status=400
            )

        day = current_dp.day_id
        journey = day.journey_id

        # =====================================================
        # 🔐 REQUIRED ITEMS CHECK (Prayer, Devotion, Action, Quiz)
        # =====================================================
        REQUIRED_ITEMS = ["prayer", "devotion", "action", "quiz"]

        completed_items = UserDayItemProgress.objects.filter(
            user=user,
            day=day,
            item_type__in=REQUIRED_ITEMS,
            completed=True
        ).values_list("item_type", flat=True)

        if not set(REQUIRED_ITEMS).issubset(set(completed_items)):
            return Response(
                {
                    "error": "Complete all required items before finishing the day",
                    "required_items": REQUIRED_ITEMS,
                    "completed_items": list(completed_items)
                },
                status=400
            )

        # =====================================================
        # ✅ COMPLETE DAY
        # =====================================================
        current_dp.status = "completed"
        current_dp.completed_at = today
        current_dp.save()

        # =====================================================
        # 📈 UPDATE JOURNEY PROGRESS
        # =====================================================
        journey_progress = UserJourneyProgress.objects.get(
            user=user,
            journey=journey
        )

        journey_progress.completed_days += 1
        journey_progress.save()

        # =====================================================
        # ➡️ NEXT DAY (same journey)
        # =====================================================
        next_day = Days.objects.filter(
            journey_id=journey,
            order=day.order + 1
        ).first()

        if next_day:
            UserDayProgress.objects.create(
                user=user,
                day_id=next_day,
                status="current"
            )

            return Response(
                {
                    "message": "Day completed successfully 🎉",
                    "next_day_id": next_day.id,
                    "next_day_order": next_day.order
                },
                status=200
            )

        # =====================================================
        # 🏁 JOURNEY COMPLETED
        # =====================================================
        journey_progress.status = "completed"
        journey_progress.completed = True
        journey_progress.save()

        persona = PersonaJourney.objects.get(persona=user.category)
        sequence = persona.sequence
        current_index = sequence.index(journey.id)

        # =====================================================
        # ➡️ NEXT JOURNEY OR RESET
        # =====================================================
        if current_index + 1 < len(sequence):
            next_journey = Journey.objects.get(id=sequence[current_index + 1])
        else:
            # 🔄 RESET ALL PROGRESS
            UserDayProgress.objects.filter(user=user).delete()
            UserJourneyProgress.objects.filter(user=user).delete()
            UserDayItemProgress.objects.filter(user=user).delete()

            next_journey = Journey.objects.get(id=sequence[0])

        # =====================================================
        # ▶️ START NEXT JOURNEY
        # =====================================================
        new_journey_progress = UserJourneyProgress.objects.create(
            user=user,
            journey=next_journey,
            status="current",
            completed_days=0,
            completed=False
        )

        first_day = Days.objects.filter(
            journey_id=next_journey,
            order=1
        ).first()

        UserDayProgress.objects.create(
            user=user,
            day_id=first_day,
            status="current"
        )

        return Response(
            {
                "message": "Journey completed 🎯 New journey started",
                "new_journey_id": next_journey.id,
                "first_day_id": first_day.id
            },
            status=200
        )




class CompleteDayItemView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def post(self, request):
        user = request.user
        item_type = request.data.get("item_type")   # prayer / devotion / action
        day_id = request.data.get("day_id")

        # 🔹 validate item_type using if / elif
        if item_type == "prayer":
            pass
        elif item_type == "devotion":
            pass
        elif item_type == "action":
            pass
        else:
            return Response(
                {"error": "Invalid item_type. Use prayer / devotion / action"},
                status=400
            )

        # 🔹 validate day_id
        if not day_id:
            return Response(
                {"error": "day_id is required"},
                status=400
            )

        day = Days.objects.filter(id=day_id).first()
        if not day:
            return Response(
                {"error": "Invalid day_id"},
                status=404
            )

        # 🔹 ensure this is CURRENT day for user
        current_dp = UserDayProgress.objects.filter(
            user=user,
            day_id=day,
            status="current"
        ).first()

        if not current_dp:
            return Response(
                {"error": "You can only complete items for the current day"},
                status=400
            )

        # 🔹 create/update item progress
        obj, created = UserDayItemProgress.objects.get_or_create(
            user=user,
            day=day,
            item_type=item_type
        )

        if obj.completed:
            return Response({
                "message": f"{item_type} already completed",
                "day_id": day.id,
                "completed": True
            }, status=200)

        obj.completed = True
        obj.completed_at = timezone.now()
        obj.save()

        return Response({
            "message": f"{item_type} completed successfully",
            "day_id": day.id,
            "item_type": item_type,
            "completed": True
        }, status=200)
