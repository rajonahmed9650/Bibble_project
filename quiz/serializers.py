from rest_framework import serializers
from .models import DailyQuiz,QuizAnswerOption,QuizAnswer
import requests

class QuizAnswerOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuizAnswerOption
        fields = ["id", "daily_quiz_id", "option", "is_correct"]

    def validate(self, data):
        quiz_id = data.get("daily_quiz_id")
        option_text = data.get("option")
        is_correct = data.get("is_correct", False)

        # ---- SAFETY FIRST (required fields check) ----
        if not quiz_id:
            raise serializers.ValidationError({
                "daily_quiz_id": "Quiz ID is required."
            })

        if not option_text:
            raise serializers.ValidationError({
                "option": "Option text is required."
            })

        # ---- DUPLICATE OPTION CHECK ----
        if QuizAnswerOption.objects.filter(
            daily_quiz_id=quiz_id,
            option__iexact=option_text
        ).exists():
            raise serializers.ValidationError({
                "option": "This option already exists for this quiz."
            })

        # ---- ONLY ONE CORRECT OPTION CHECK ----
        if is_correct:
            if QuizAnswerOption.objects.filter(
                daily_quiz_id=quiz_id,
                is_correct=True
            ).exists():
                raise serializers.ValidationError({
                    "is_correct": "Only ONE correct option allowed for each quiz."
                })

        # ********** MOST IMPORTANT LINE **********
        return data

    class Meta:
        model = QuizAnswerOption
        fields = ["id", "daily_quiz_id", "option", "is_correct"]

class QuizAnswerOptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswerOption
        fields = ["id", "option"]


class DailyQuizSerializer(serializers.ModelSerializer):
    options = QuizAnswerOptionSerializer(many = True,read_only = True)
    class Meta:
        model = DailyQuiz
        fields = ["id","journey_id","days_id","question","options"]

    def validate(self, data):
        question = data.get("question")
        if DailyQuiz.objects.filter(question=question).exists():
            raise serializers.ValidationError({"question":"This question already exists"})
        return data        


# class QuizAnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QuizAnswer
#         fields = ["id","daily_quiz_id","user_id","quiz_answer_option_id","points"]


class QuizAnswerSubmitSerializer(serializers.ModelSerializer):
    daily_quiz_id = serializers.IntegerField()
    quiz_answer_option_id = serializers.IntegerField()

    class Meta:
        model = QuizAnswer
        fields = ["daily_quiz_id", "quiz_answer_option_id"]

    def validate(self, data):
        quiz_id = data["daily_quiz_id"]
        option_id = data["quiz_answer_option_id"]

        # Validate quiz exists
        try:
            quiz = DailyQuiz.objects.get(id=quiz_id)
        except DailyQuiz.DoesNotExist:
            raise serializers.ValidationError({"daily_quiz_id": "Quiz not found."})

        # Validate option exists
        try:
            option = QuizAnswerOption.objects.get(id=option_id)
        except QuizAnswerOption.DoesNotExist:
            raise serializers.ValidationError({"quiz_answer_option_id": "Option not found."})

        # Option must belong to quiz
        if option.daily_quiz_id_id != quiz.id:
            raise serializers.ValidationError({
                "quiz_answer_option_id": "This option does not belong to this quiz."
            })

        data["quiz"] = quiz
        data["option"] = option
        return data

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        quiz = validated_data["quiz"]
        option = validated_data["option"]

        is_correct = option.is_correct
        points = 1 if is_correct else 0

        # Save to database (must use ForeignKey field names)
        answer = QuizAnswer.objects.create(
            daily_quiz_id=quiz,
            quiz_answer_option_id=option,
            user_id=user,
            points=points
        )

        return {
            "correct": is_correct,
            "points": points
        }

