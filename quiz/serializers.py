from rest_framework import serializers
from .models import DailyQuiz,QuizAnswerOption,QuizAnswer
import requests

class QuizAnswerOptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswerOption
        fields = ["option", "is_correct"]

class QuizAnswerOptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswerOption
        fields = ["id", "option"]


class DailyQuizCreateSerializer(serializers.ModelSerializer):
    options = QuizAnswerOptionWriteSerializer(many=True)

    class Meta:
        model = DailyQuiz
        fields = ["id","journey_id", "days_id", "question", "options"]

    # ---------------------------
    # VALIDATION AREA
    # ---------------------------
    def validate(self, data):
        journey = data.get("journey_id")
        day = data.get("days_id")
        question = data.get("question")
        options = data.get("options")

        # 1️⃣ Duplicate question block
        if DailyQuiz.objects.filter(
            journey_id=journey,
            days_id=day,
            question__iexact=question
        ).exists():
            raise serializers.ValidationError({
                "question": "This question already exists for this day."
            })

        # 2️⃣ Count correct answers
        correct_count = sum([1 for opt in options if opt.get("is_correct")])

        if correct_count == 0:
            raise serializers.ValidationError({
                "options": "At least ONE option must be correct."
            })

        if correct_count > 1:
            raise serializers.ValidationError({
                "options": "Only ONE option can be correct."
            })

        return data

    # ---------------------------
    # CREATE AREA
    # ---------------------------
    def create(self, validated_data):
        options_data = validated_data.pop("options")
        quiz = DailyQuiz.objects.create(**validated_data)

        for opt in options_data:
            QuizAnswerOption.objects.create(
                daily_quiz_id=quiz,
                **opt
            )

        return quiz

    

class DailyQuizReadSerializer(serializers.ModelSerializer):
    options = QuizAnswerOptionReadSerializer(many=True)

    class Meta:
        model = DailyQuiz
        fields = ["id", "journey_id", "days_id", "question", "options"]



from django.db import models

class MultipleQuizAnswerSubmitSerializer(serializers.Serializer):
    answers = serializers.ListField()

    def validate(self, data):
        validated = []

        for ans in data["answers"]:
            quiz_id = ans.get("daily_quiz_id")
            option_id = ans.get("quiz_answer_option_id")

            # Check quiz
            try:
                quiz = DailyQuiz.objects.get(id=quiz_id)
            except DailyQuiz.DoesNotExist:
                raise serializers.ValidationError({"daily_quiz_id": f"Quiz {quiz_id} not found"})

            # Check option
            try:
                option = QuizAnswerOption.objects.get(id=option_id)
            except QuizAnswerOption.DoesNotExist:
                raise serializers.ValidationError({"quiz_answer_option_id": f"Option {option_id} not found"})

            # Check relation
            if option.daily_quiz_id_id != quiz.id:
                raise serializers.ValidationError({
                    "quiz_answer_option_id": "Option does not belong to the quiz"
                })

            validated.append((quiz, option))

        return {"validated": validated}

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        total_points = 0
        validated = validated_data["validated"]

        # Save all answers
        for quiz, option in validated:
            point = 1 if option.is_correct else 0
            total_points += point

            QuizAnswer.objects.create(
                daily_quiz_id=quiz,
                quiz_answer_option_id=option,
                user_id=user,
                points=point
            )

        # Count total points for SAME DAY
        day = validated[0][0].days_id
        day_points = QuizAnswer.objects.filter(
            user_id=user,
            daily_quiz_id__days_id=day
        ).aggregate(total=models.Sum("points"))["total"] or 0

        return {
            "user_id": user.id,
            "total_points_for_day": day_points,
            # "answers_saved": len(validated)
        }
