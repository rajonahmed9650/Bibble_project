# progress/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.permissions import HasActiveSubscription
from journey.models import PersonaJourney, Days
from userprogress.models import UserJourneyProgress, UserDayProgress
from userprogress.utils import get_current_day

from daily_devotion.models import DailyDevotion, DailyPrayer, MicroAction
from daily_devotion.serializers import (
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer
)
from quiz.models import DailyQuiz
from quiz.serializers import DailyQuizReadSerializer


# progress/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.permissions import HasActiveSubscription
from journey.models import PersonaJourney, Days
from userprogress.models import UserJourneyProgress, UserDayProgress
from userprogress.utils import get_current_day

from daily_devotion.models import DailyDevotion, DailyPrayer, MicroAction
from daily_devotion.serializers import (
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer
)
from quiz.models import DailyQuiz
from quiz.serializers import DailyQuizReadSerializer


class TodayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get(self, request):
        user = request.user

        if not user.category:
            return Response({"message": "No category found"}, status=200)

        persona = PersonaJourney.objects.filter(persona=user.category).first()
        if not persona:
            return Response({"message": "No persona configuration"}, status=200)

        sequence = persona.sequence

        # ✅ ensure only one CURRENT journey from sequence
        progress = UserJourneyProgress.objects.filter(
            user=user,
            status="current",
            journey_id__in=sequence
        ).first()

        if not progress:
            progress, _ = UserJourneyProgress.objects.get_or_create(
                user=user,
                journey_id=sequence[0],
                defaults={"status": "current"}
            )

        # ✅ get current day
        current_day = get_current_day(user, progress.journey)

        if not current_day:
            first_day = Days.objects.filter(
                journey_id=progress.journey,
                order=1
            ).first()

            UserDayProgress.objects.get_or_create(
                user=user,
                day_id=first_day,
                defaults={"status": "current"}
            )
            current_day = first_day

        return Response({
            "journey": {
                "id": progress.journey.id,
                "name": progress.journey.name,
                "status": progress.status
            },
            "day": {
                "id": current_day.id,
                "order": current_day.order,
                "title": current_day.name
            },
            "prayer": DailyPrayerSerializer(
                DailyPrayer.objects.filter(day_id=current_day).first()
            ).data if DailyPrayer.objects.filter(day_id=current_day).exists() else None,
            "devotion": DailyDevotionSerializer(
                DailyDevotion.objects.filter(day_id=current_day).first()
            ).data if DailyDevotion.objects.filter(day_id=current_day).exists() else None,
            "action": MicroActionSerializer(
                MicroAction.objects.filter(day_id=current_day).first()
            ).data if MicroAction.objects.filter(day_id=current_day).exists() else None,
            "quiz": DailyQuizReadSerializer(
                DailyQuiz.objects.filter(days_id=current_day),
                many=True
            ).data
        }, status=200)



# progress/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from payments.permissions import HasActiveSubscription
from journey.models import Journey, Days, PersonaJourney
from userprogress.models import UserJourneyProgress, UserDayProgress


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from payments.permissions import HasActiveSubscription
from journey.models import Journey, Days, PersonaJourney
from userprogress.models import UserJourneyProgress, UserDayProgress



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from payments.permissions import HasActiveSubscription
from journey.models import Journey, Days, PersonaJourney
from userprogress.models import UserJourneyProgress, UserDayProgress


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from payments.permissions import HasActiveSubscription
from journey.models import Journey, Days, PersonaJourney
from userprogress.models import UserJourneyProgress, UserDayProgress


class CompleteDayView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    @transaction.atomic
    def post(self, request):
        user = request.user

        journey_id = request.data.get("journey_id")
        day_id = request.data.get("day_id")
        action = request.data.get("action")

        if not journey_id or not day_id or action != "complete":
            return Response(
                {"error": "journey_id, day_id and action='complete' are required"},
                status=400
            )

        journey = Journey.objects.filter(id=journey_id).first()
        if not journey:
            return Response({"error": "Invalid journey"}, status=404)

        day = Days.objects.filter(id=day_id, journey_id=journey).first()
        if not day:
            return Response({"error": "Invalid day for this journey"}, status=404)

        # 🔑 ensure current day (auto-init safety)
        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current",
            day_id__journey_id=journey
        ).select_related("day_id").first()

        if not current_dp:
            first_day = Days.objects.filter(
                journey_id=journey,
                order=1
            ).first()

            current_dp, _ = UserDayProgress.objects.get_or_create(
                user=user,
                day_id=first_day,
                defaults={"status": "current"}
            )

        # day_id must match current
        if current_dp.day_id.id != day.id:
            return Response(
                {
                    "error": "You can only complete the current day",
                    "current_day_id": current_dp.day_id.id,
                    "received_day_id": day.id
                },
                status=400
            )

        # complete day
        current_dp.status = "completed"
        current_dp.save()

        progress, _ = UserJourneyProgress.objects.get_or_create(
            user=user,
            journey=journey,
            defaults={"status": "current"}
        )

        progress.completed_days += 1
        progress.save()

        # next day
        next_day = Days.objects.filter(
            journey_id=journey,
            order=day.order + 1
        ).first()

        if next_day:
            ndp, _ = UserDayProgress.objects.get_or_create(
                user=user,
                day_id=next_day
            )
            ndp.status = "current"
            ndp.save()

            return Response({"message": "Next day unlocked"}, status=200)

        # journey completed
        progress.status = "completed"
        progress.completed = True
        progress.save()

        persona = PersonaJourney.objects.get(persona=user.category)
        sequence = persona.sequence
        index = sequence.index(journey.id)

        # next journey
        if index + 1 < len(sequence):
            next_journey = Journey.objects.get(id=sequence[index + 1])

            next_progress, _ = UserJourneyProgress.objects.get_or_create(
                user=user,
                journey=next_journey,
                defaults={"status": "current"}
            )
            next_progress.completed_days = 0
            next_progress.completed = False
            next_progress.status = "current"
            next_progress.save()

            first_day = Days.objects.filter(
                journey_id=next_journey,
                order=1
            ).first()

            UserDayProgress.objects.get_or_create(
                user=user,
                day_id=first_day,
                defaults={"status": "current"}
            )

            return Response({"message": "Next journey started"}, status=200)

        # reset all
        UserDayProgress.objects.filter(user=user).delete()
        UserJourneyProgress.objects.filter(user=user).delete()

        first_journey = Journey.objects.get(id=sequence[0])
        restart_progress = UserJourneyProgress.objects.create(
            user=user,
            journey=first_journey,
            status="current"
        )

        first_day = Days.objects.filter(
            journey_id=first_journey,
            order=1
        ).first()

        UserDayProgress.objects.create(
            user=user,
            day_id=first_day,
            status="current"
        )

        return Response(
            {"message": "All journeys completed. Restarted from beginning."},
            status=200
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from journey.models import Journey, Days
from userprogress.models import UserDayProgress


class UserProgressDaysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, journey_id):
        user = request.user

        journey = Journey.objects.filter(id=journey_id).first()
        if not journey:
            return Response({"message": "Journey not found"}, status=404)

        days = Days.objects.filter(
            journey_id=journey
        ).order_by("order")

        result = []

        for day in days:
            dp = UserDayProgress.objects.filter(
                user=user,
                day_id=day
            ).first()

            result.append({
                "day_id": day.id,
                "day_name": day.name,
                "day_order": day.order,
                "status": dp.status if dp else "locked"
            })

        return Response({
            "journey": {
                "id": journey.id,
                "name": journey.name
            },
            "days": result
        }, status=200)
