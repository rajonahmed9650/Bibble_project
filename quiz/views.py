from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import QuizAnswer
from .models import DailyQuiz, QuizAnswerOption
from .serializers import (
    DailyQuizCreateSerializer,
    DailyQuizReadSerializer,
    QuizAnswerOptionWriteSerializer,
    QuizAnswerOptionReadSerializer,
    MultipleQuizAnswerSubmitSerializer
)


# -------------------------------
# QUIZ LIST + CREATE
# -------------------------------
class DailyQuizListCreate(APIView):

    def get(self, request):
        quizzes = DailyQuiz.objects.all()
        serializer = DailyQuizReadSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DailyQuizCreateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "All quizzes created successfully"}, status=201)


# -------------------------------
# QUIZ DETAIL
# -------------------------------
class DailyQuizDetail(APIView):

    def get(self, request, pk):
        quiz = get_object_or_404(DailyQuiz, pk=pk)
        serializer = DailyQuizReadSerializer(quiz)
        return Response(serializer.data)

    def put(self, request, pk):
        quiz = get_object_or_404(DailyQuiz, pk=pk)
        serializer = DailyQuizCreateSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Quiz updated"})
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        quiz = get_object_or_404(DailyQuiz, pk=pk)
        quiz.delete()
        return Response({"message": "Quiz deleted"})


# -------------------------------
# OPTION LIST + CREATE
# -------------------------------
class QuizOptionListCreate(APIView):

    def get(self, request):
        options = QuizAnswerOption.objects.all()
        serializer = QuizAnswerOptionReadSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizAnswerOptionWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Option created successfully"}, status=201)
        return Response(serializer.errors, status=400)


# -------------------------------
# OPTION DETAIL
# -------------------------------
class QuizOptionDetail(APIView):

    def get(self, request, pk):
        option = get_object_or_404(QuizAnswerOption, pk=pk)
        serializer = QuizAnswerOptionReadSerializer(option)
        return Response(serializer.data)

    def put(self, request, pk):
        option = get_object_or_404(QuizAnswerOption, pk=pk)
        serializer = QuizAnswerOptionWriteSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Option updated successfully"})
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        option = get_object_or_404(QuizAnswerOption, pk=pk)
        option.delete()
        return Response({"message": "Option deleted successfully"})


# -------------------------------
# SUBMIT ANSWER
# -------------------------------
from django.utils import timezone
from userprogress.models import UserDayItemProgress, UserDayProgress


class MultipleSubmitQuizAnswer(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        current_dp = UserDayProgress.objects.filter(
            user=user,
            status="current"
        ).select_related("day_id").first()

        if not current_dp:
            return Response({"error": "No active day"}, status=400)

        # DELETE old answers (important)
        QuizAnswer.objects.filter(
            user_id=user,
            daily_quiz_id__days_id=current_dp.day_id
        ).delete()

        #  Save new answers
        serializer = MultipleQuizAnswerSubmitSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Quiz progress
        quiz_progress, _ = UserDayItemProgress.objects.get_or_create(
            user=user,
            day=current_dp.day_id,
            item_type="quiz"
        )

        quiz_progress.completed = True
        quiz_progress.completed_at = timezone.now()
        quiz_progress.save()

        # Recalculate points
        points = QuizAnswer.objects.filter(
            user_id=user,
            daily_quiz_id__days_id=current_dp.day_id,
            points=1
        ).count()

        return Response({
            "message": "Quiz submitted successfully",
            "points_added": points
        }, status=200)


