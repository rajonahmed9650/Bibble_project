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





class MultipleQuizAnswerSubmitSerializer(serializers.Serializer):
    answers = serializers.ListField()

    def validate(self, data):
        validated = []

        for ans in data["answers"]:
            quiz_id = ans.get("daily_quiz_id")
            option_id = ans.get("quiz_answer_option_id")

            quiz = DailyQuiz.objects.get(id=quiz_id)
            option = QuizAnswerOption.objects.get(id=option_id)

            if option.daily_quiz_id_id != quiz.id:
                raise serializers.ValidationError(
                    "Option does not belong to the quiz"
                )

            validated.append((quiz, option))

        return {"validated": validated}

    def create(self, validated_data):
        user = self.context["request"].user
        validated = validated_data["validated"]

        for quiz, option in validated:
            # ✅ ANSWER UPDATE OR CREATE (CHANGE ALLOWED)
            QuizAnswer.objects.update_or_create(
                daily_quiz_id=quiz,
                user_id=user,
                defaults={
                    "quiz_answer_option_id": option,
                    "points": 1 if option.is_correct else 0
                }
            )

        return {
            "submitted": len(validated)
        }

