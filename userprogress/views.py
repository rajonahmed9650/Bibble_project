
# progress/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.permissions import HasActiveSubscription
from journey.models import PersonaJourney, Days,JourneyDetails
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

        # -----------------------------
        # 1️⃣ Category check
        # -----------------------------
        if not user.category:
            return Response(
                {"error": "User category not assigned"},
                status=400
            )

        # -----------------------------
        # 2️⃣ Current journey (SAFE)
        # -----------------------------
        journey_progress = UserJourneyProgress.objects.filter(
            user=user,
            status="current"
        ).select_related("journey").first()

        if not journey_progress:
            return Response(
                {"error": "No active journey. Please complete onboarding."},
                status=400
            )

        journey = journey_progress.journey

        # -----------------------------
        # 3️⃣ Current day (SAFE)
        # -----------------------------
        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current",
            day_id__journey_id=journey
        ).select_related("day_id").first()

        if not current_dp:
            return Response(
                {"error": "No current day"},
                status=400
            )

        day = current_dp.day_id

        # -----------------------------
        # 4️⃣ Step progress
        # -----------------------------
        step_progress = UserDayItemProgress.objects.filter(
            user=user,
            day=day,
            item_type=step
        ).first()

        # -----------------------------
        # 5️⃣ Step content
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

        return Response(
            {
                "journey": {
                    "id": journey.id,
                    "name": journey.name,
                    "status": journey_progress.status
                },
                "day": {
                    "id": day.id,
                    "order": day.order,
                    "title": day.name,
                    "status": current_dp.status
                },
                "is_completed": step_progress.completed if step_progress else False,
                "data": data
            },
            status=200
        )



class UserProgressDaysView(APIView):
    permission_classes = [IsAuthenticated,HasActiveSubscription]

    def get(self, request, journey_id):
        user = request.user
        if not Days.objects.filter(journey_id=journey_id).exists():
            return Response(
                {"error": "Journey not found or has no days"},
                status=404
            )
        journey = Journey.objects.get(id=journey_id)
        journey_details = JourneyDetails.objects.filter(
            journey_id=journey_id
        ).first()


        image_url = (
            request.build_absolute_uri(journey_details.image.url)
            if journey_details and journey_details.image
            else None
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
        is_new_user = not UserDayProgress.objects.filter(user=user).exists()


        result = []
        for day in days:
            status = dp_map.get(day.id)
            if not status:
                if is_new_user and day.order == 1:
                    status = "current"
                else:
                    status = "locked"
            result.append({
                "day_id": day.id,
                "day_name": day.name,
                "order": day.order,
                "status": status
            })

        return Response({
            "journey": {
                "id": journey.id,
                "name": journey.name,
            },
            "journey_details": {
                "image": image_url,
                "details": journey_details.details if journey_details else None,
            },
            "days": result
        })


from journey.models import Days, Journey, PersonaJourney
from daily_devotion.models import DailyReflectionSpace


from django.utils import timezone
from django.db import transaction

from notifications.utils import create_notification
from datetime import timedelta


class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    @transaction.atomic
    def post(self, request):
        user = request.user
        now = timezone.now()

        # -----------------------------
        # 0️⃣ day_id mandatory
        # -----------------------------
        day_id = request.data.get("day_id")
        if not day_id:
            return Response({"error": "day_id is required"}, status=400)

        # -----------------------------
        # 1️⃣ Testing rule (2 min)
        # -----------------------------
        two_minutes_ago = now - timedelta(minutes=2)
        if UserDayProgress.objects.filter(
            user=user,
            completed_at__gte=two_minutes_ago
        ).exists():
            return Response(
                {"error": "Testing mode: wait 2 minutes before next day"},
                status=400
            )

        # -----------------------------
        # 2️⃣ Current journey
        # -----------------------------
        journey_progress = UserJourneyProgress.objects.filter(
            user=user,
            status="current"
        ).select_related("journey").first()

        if not journey_progress:
            return Response(
                {"error": "No active journey. Please complete onboarding."},
                status=400
            )

        journey = journey_progress.journey

        # -----------------------------
        # 3️⃣ Current day
        # -----------------------------
        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current",
            day_id__journey_id=journey
        ).select_related("day_id").first()

        if not current_dp:
            return Response({"error": "No current day"}, status=400)

        # -----------------------------
        # 4️⃣ Validate day_id
        # -----------------------------
        if int(day_id) != current_dp.day_id.id:
            return Response(
                {"error": "Invalid day. This is not the current day"},
                status=400
            )

        day = current_dp.day_id

        # -----------------------------
        # 5️⃣ Required items
        # -----------------------------
        REQUIRED_ITEMS = ["prayer", "devotion", "action", "quiz"]

        completed_items = UserDayItemProgress.objects.filter(
            user=user,
            day=day,
            item_type__in=REQUIRED_ITEMS,
            completed=True
        ).values_list("item_type", flat=True)

        if not set(REQUIRED_ITEMS).issubset(set(completed_items)):
            return Response(
                {"error": "Complete all required items first"},
                status=400
            )

        # -----------------------------
        # 6️⃣ Complete current day
        # -----------------------------
        current_dp.status = "completed"
        current_dp.completed_at = now
        current_dp.save()

        journey_progress.completed_days += 1
        journey_progress.save()

        create_notification(
            user=user,
            title="Day Completed 🎉",
            message=f"You have completed Day {day.order}: {day.name}",
            n_type="journey"
        )
        # -----------------------------
        # 7️⃣ Next day (same journey)
        # -----------------------------
        next_day = Days.objects.filter(
            journey_id=journey,
            order=day.order + 1
        ).first()

        if next_day:
            UserDayProgress.objects.update_or_create(
                user=user,
                day_id=next_day,
                defaults={"status": "current", "completed_at": None}
            )

            return Response(
                {
                    "message": "Day completed 🎉 Next day is current",
                    "current_day_id": next_day.id
                },
                status=200
            )

        # =================================================
        # 8️⃣ JOURNEY COMPLETED → MOVE TO NEXT JOURNEY
        # =================================================
        journey_progress.status = "completed"
        journey_progress.completed = True
        journey_progress.save()

        create_notification(
            user=user,
            title="Journey Completed 🎯",
            message=f"Congratulations! You completed the journey: {journey.name}",
            n_type="journey"
        )

        persona = PersonaJourney.objects.filter(
            persona=user.category
        ).first()

        if not persona or not persona.sequence:
            return Response({"message": "Journey completed 🎯"}, status=200)

        sequence = persona.sequence
        if journey.id not in sequence:
            return Response({"message": "Journey completed 🎯"}, status=200)

        current_index = sequence.index(journey.id)

        # -----------------------------
        # 9️⃣ Next journey
        # -----------------------------
        if current_index + 1 < len(sequence):
            next_journey_id = sequence[current_index + 1]
            next_journey = Journey.objects.get(id=next_journey_id)

            UserJourneyProgress.objects.update_or_create(
                user=user,
                journey=next_journey,
                defaults={
                    "status": "current",
                    "completed": False,
                    "completed_days": 0
                }
            )

            first_day = Days.objects.filter(
                journey_id=next_journey,
                order=1
            ).first()

            if first_day:
                UserDayProgress.objects.update_or_create(
                    user=user,
                    day_id=first_day,
                    defaults={"status": "current"}
                )

            return Response(
                {
                    "message": "Journey completed 🎯 Next journey started",
                    "new_journey_id": next_journey.id,
                    "current_day_id": first_day.id if first_day else None
                },
                status=200
            )

        return Response({"message": "All journeys completed 🎉"}, status=200)





from .models import (
    Days,
    jourenystepitem,
    UserDayProgress,
    UserDayItemProgress
)


# userprogress/views.py
class CompleteDayItemView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def post(self, request):
        user = request.user
        item_type = request.data.get("item_type")  # prayer/devotion/action/reflection
        day_id = request.data.get("day_id")

        if not item_type or not day_id:
            return Response(
                {"error": "item_type and day_id are required"},
                status=400
            )

        day = Days.objects.filter(id=day_id).first()
        if not day:
            return Response({"error": "Invalid day"}, status=400)

        # ✅ only CURRENT day allowed
        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current",
            day_id=day
        ).first()

        if not current_dp:
            return Response(
                {"error": "Only current day items can be completed"},
                status=400
            )

        # ✅ USER PROGRESS TABLE
        obj, created = UserDayItemProgress.objects.get_or_create(
            user=user,
            day=day,
            item_type=item_type
        )

        if obj.completed:
            return Response(
                {"message": f"{item_type} already completed"},
                status=200
            )

        obj.completed = True
        obj.completed_at = timezone.now()
        obj.save()

        return Response(
            {
                "message": f"{item_type} completed successfully",
                "day_id": day.id,
                "item_type": item_type,
                "completed": True
            },
            status=200
        )


from .models import jourenystepitem
from .serializers import JourneyStepItemSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404

class allstepviews(APIView):
    permission_classes = [IsAuthenticated,HasActiveSubscription]
    def get(self, request, journey_id, day_id):
        user = request.user
        day = get_object_or_404(Days, id=day_id, journey_id=journey_id)
        steps = jourenystepitem.objects.filter(
            journey_id=journey_id,
            days_id=day_id
        )

        serializer = JourneyStepItemSerializer(steps, many=True)
        return Response({
            "user_id": user.id,
            "journey_id": journey_id,
            "day_id": day_id,
            "day_title": day.name,   # day title এখানে
            "steps": serializer.data
        })
    def post(self, request, journey_id, day_id):
        data = request.data.copy()
        data["journey_id"] = journey_id
        data["days_id"] = day_id

        serializer = JourneyStepItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Step created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

     