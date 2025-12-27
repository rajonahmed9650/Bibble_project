
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

# userprogress/views.py
class TodayStepView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    ALLOWED_STEPS = ["prayer", "devotion", "action", "quiz"]

    def get(self, request, step):
        user = request.user

        if not user.category:
            return Response({"error": "User category not assigned"}, status=400)

        if step not in self.ALLOWED_STEPS:
            return Response({"error": "Invalid step"}, status=400)

        day_id = request.query_params.get("day_id")

        # ===============================
        # CASE 1: Completed / Current day (day_id provided)
        # ===============================
        if day_id:
            try:
                day = Days.objects.select_related("journey_id").get(id=day_id)
            except Days.DoesNotExist:
                return Response({"error": "Day not found"}, status=404)

            current_dp = UserDayProgress.objects.filter(
                user=user,
                day_id=day,
                status__in=["current", "completed"]
            ).first()

            if not current_dp:
                return Response({"error": "This day is locked"}, status=403)

            journey = day.journey_id
            journey_progress = UserJourneyProgress.objects.filter(
                user=user,
                journey=journey
            ).first()

        # ===============================
        # CASE 2: Current day (default)
        # ===============================
        else:
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

            current_dp = UserDayProgress.objects.filter(
                user=user,
                status="current",
                day_id__journey_id=journey
            ).select_related("day_id").first()

            if not current_dp:
                return Response({"error": "No current day"}, status=400)

            day = current_dp.day_id

        # ===============================
        # STEP PROGRESS
        # ===============================
        step_progress = UserDayItemProgress.objects.filter(
            user=user,
            day=day,
            item_type=step
        ).first()

        # ===============================
        # CONTENT
        # ===============================
        if step == "prayer":
            obj = DailyPrayer.objects.filter(day_id=day).first()
            data = DailyPrayerSerializer(obj, context={"request": request}).data if obj else None

        elif step == "devotion":
            obj = DailyDevotion.objects.filter(day_id=day).first()
            data = DailyDevotionSerializer(obj, context={"request": request}).data if obj else None

        elif step == "action":
            obj = MicroAction.objects.filter(day_id=day,journey_id=journey).first()
            data = MicroActionSerializer(obj, context={"request": request}).data if obj else None

        elif step == "quiz":
            quizzes = DailyQuiz.objects.filter(days_id=day)
            data = DailyQuizReadSerializer(quizzes, many=True).data

        # ===============================
        # RESPONSE (UNCHANGED)
        # ===============================
        return Response({
            "journey": {
                "id": journey.id,
                "name": journey.name,
                "status": journey_progress.status if journey_progress else None
            },
            "day": {
                "id": day.id,
                "order": day.order,
                "title": day.name,
                "status": current_dp.status
            },
            "is_completed": step_progress.completed if step_progress else False,
            "data": data
        })



class UserProgressDaysView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

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

        # ✅ journey-wise new user check
        is_new_user = not UserDayProgress.objects.filter(
            user=user,
            day_id__journey_id=journey_id
        ).exists()

        result = []

        for day in days:
            status = dp_map.get(day.id)

            if not status:
                if is_new_user and day.order == 1:
                    # ✅ DB + response sync
                    UserDayProgress.objects.create(
                        user=user,
                        day_id=day,
                        status="current"
                    )
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




from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from journey.models import Journey, Days, PersonaJourney
from daily_devotion.models import DailyDevotion, DailyReflectionSpace
from notifications.utils import create_notification
from userprogress.models import (
    UserJourneyProgress,
    UserDayProgress,
    UserDayItemProgress
)


class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    @transaction.atomic
    def post(self, request):
        user = request.user
        now = timezone.now()

        journey_id = request.data.get("journey_id")
        day_id = request.data.get("day_id")
        action = request.data.get("action")
        reflection_note = request.data.get("reflection_note","").strip()

        if not journey_id or not day_id or action != "complete":
            return Response(
                {"error": "journey_id, day_id, action='complete' required"},
                status=400
            )

        # ⏱ TESTING RULE
        if UserDayProgress.objects.filter(
            user=user,
            completed_at__gte=now - timedelta(minutes=2)
        ).exists():
            return Response({"error": "Wait 5 minutes"}, status=400)

        #  CURRENT JOURNEY
        journey_progress = UserJourneyProgress.objects.filter(
            user=user,
            status="current"
        ).select_related("journey").first()

        if not journey_progress:
            return Response({"error": "No active journey"}, status=400)

        journey = journey_progress.journey
        if int(journey_id) != journey.id:
            return Response({"error": "Invalid journey"}, status=400)

        #  CURRENT DAY
        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current",
            day_id__journey_id=journey
        ).select_related("day_id").first()

        if not current_dp or int(day_id) != current_dp.day_id.id:
            return Response({"error": "Invalid day"}, status=400)

        day = current_dp.day_id

        #  STEP VALIDATION
        REQUIRED = ["prayer","devotion","action","quiz"]
        completed = UserDayItemProgress.objects.filter(
            user=user,
            day=day,
            item_type__in=REQUIRED,
            completed=True
        ).values_list("item_type", flat=True)

        if not set(REQUIRED).issubset(set(completed)):
            return Response(
                {
                    "error": "Complete all steps first",
                    "required": REQUIRED,
                    "completed": list(completed)
                },
                status=400
            )

        # 📝 REFLECTION SAVE
        if reflection_note:
            devotion = DailyDevotion.objects.filter(day_id=day).first()
            if devotion:
                DailyReflectionSpace.objects.create(
                    user=user,
                    dailydevotion_id=devotion,
                    reflection_note=reflection_note
                )

                UserDayItemProgress.objects.update_or_create(
                    user=user,
                    day=day,
                    item_type="reflection",
                    defaults={"completed": True}
                )

        # ✅ COMPLETE DAY
        current_dp.status = "completed"
        current_dp.completed_at = now
        current_dp.save()

        journey_progress.completed_days += 1
        journey_progress.save()

        create_notification(
            user=user,
            title="Day Completed 🎉",
            message=f"Day {day.order} completed",
            n_type="journey"
        )

        # ➡️ NEXT DAY
        next_day = Days.objects.filter(
            journey_id=journey,
            order=day.order + 1
        ).first()

        if next_day:
            UserDayProgress.objects.update_or_create(
                user=user,
                day_id=next_day,
                defaults={"status":"current","completed_at":None}
            )
            return Response({
                "message": "Day completed 🎉 Next day is current",
                "current_day_id": next_day.id
                },
                status=200
            )

        # 🏁 JOURNEY COMPLETED
        journey_progress.status = "completed"
        journey_progress.completed = True
        journey_progress.save()

        create_notification(
            user=user,
            title="Journey Completed 🎯",
            message=f"You completed {journey.name}",
            n_type="journey"
        )

        persona = PersonaJourney.objects.filter(persona=user.category).first()
        seq = persona.sequence
        idx = seq.index(journey.id)

        if idx + 1 < len(seq):
            next_journey = Journey.objects.get(id=seq[idx+1])

            UserJourneyProgress.objects.filter(user=user).exclude(journey=journey).update(status="locked")

            UserJourneyProgress.objects.update_or_create(
                user=user,
                journey=next_journey,
                defaults={"status":"current","completed":False,"completed_days":0}
            )

            first_day = Days.objects.filter(
                journey_id=next_journey,
                order=1
            ).first()

            if first_day:
                UserDayProgress.objects.update_or_create(
                    user=user,
                    day_id=first_day,
                    defaults={"status":"current"}
                )

            return Response({
                "message": "Journey completed 🎯 Next journey started",
                "new_journey_id": next_journey.id,
                "current_day_id": first_day.id if first_day else None
            },
                status=200
            )


        return Response({"message":"All journeys completed 🎉"}, status=200)




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
        item_type = request.data.get("item_type")   # prayer/devotion/action/reflection
        day_id = request.data.get("day_id")

        STEP_SEQUENCE = ["prayer", "devotion", "action", "reflection"]

        # -------------------------
        # 1️⃣ Validate input
        # -------------------------
        if not item_type or not day_id:
            return Response(
                {"error": "item_type and day_id are required"},
                status=400
            )

        if item_type not in STEP_SEQUENCE:
            return Response({"error": "Invalid item_type"}, status=400)

        # -------------------------
        # 2️⃣ Validate day
        # -------------------------
        day = Days.objects.filter(id=day_id).first()
        if not day:
            return Response({"error": "Invalid day"}, status=400)

        # -------------------------
        # 3️⃣ Validate CURRENT day
        # -------------------------
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

        # =================================================
        # 🔥 4️⃣ SEQUENCE ENFORCEMENT (MAIN LOGIC)
        # =================================================
        step_index = STEP_SEQUENCE.index(item_type)

        if step_index > 0:
            previous_step = STEP_SEQUENCE[step_index - 1]

            prev_completed = UserDayItemProgress.objects.filter(
                user=user,
                day=day,
                item_type=previous_step,
                completed=True
            ).exists()

            if not prev_completed:
                return Response(
                    {
                        "error": f"You must complete '{previous_step}' first"
                    },
                    status=400
                )

        # -------------------------
        # 5️⃣ Create / Update step progress
        # -------------------------
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
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get(self, request, journey_id, day_id):
        user = request.user

        # -------------------------
        # -------------------------
        day = get_object_or_404(Days, id=day_id, journey_id=journey_id)

        # -------------------------
        steps = jourenystepitem.objects.filter(
            journey_id=journey_id,
            days_id=day_id
        )

        # -------------------------
        # User progress map
        # -------------------------
        progress_map = {
            p.item_type: p.completed
            for p in UserDayItemProgress.objects.filter(
                user=user,
                day=day
            )
        }

        # -------------------------
        # Merge response
        # -------------------------
        data = []
        for step in steps:
            data.append({
                "id": step.id,
                "step_name": step.step_name,
                "is_completed": progress_map.get(step.step_name, False)
            })

        return Response({
            "user_id": user.id,
            "journey_id": journey_id,
            "day_id": day_id,
            "day_title": day.name,
            "steps": data
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