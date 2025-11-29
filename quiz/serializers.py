from rest_framework import serializers
from .models import DailyQuiz,QuizAnswerOption,QuizAnswer


class QuizAnswerOptionSerializer(serializers.ModelSerializer):

    def validate(self, data):
        quiz = data.get("daily_quiz")
        option_text = data.get("option")
        is_correct = data.get("is_correct", False)

        # 1) Duplicate option check (extra friendly)
        if QuizAnswerOption.objects.filter(
                daily_quiz=quiz,
                option__iexact=option_text
        ).exists():
            raise serializers.ValidationError({
                "option": "This option already exists for this quiz."
            })

        # 2) Only one correct answer per quiz
        if is_correct:
            if QuizAnswerOption.objects.filter(
                    daily_quiz=quiz,
                    is_correct=True
            ).exists():
                raise serializers.ValidationError({
                    "is_correct": "This quiz already has a correct answer. Only one correct option is allowed."
                })

        return data

    class Meta:
        model = QuizAnswerOption
        fields = ["id", "daily_quiz", "option", "is_correct"]

class QuizAnswerOptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswerOption
        fields = ["id", "option"]


class DailyQuizSerializer(serializers.ModelSerializer):
    options = QuizAnswerOptionSerializer(many = True,read_only = True)


    class Meta:
        model = DailyQuiz
        fields = ["id","journey_id","days_id","question","options"]        


# class QuizAnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QuizAnswer
#         fields = ["id","daily_quiz_id","user_id","quiz_answer_option_id","points"]


class QuizAnswerSubmitSerializer(serializers.ModelSerializer):
    daily_quiz_id = serializers.IntegerField()
    quiz_answer_option_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = QuizAnswer
        fields = ["daily_quiz_id", "quiz_answer_option_id", "user_id"]

    def validate(self, data):
        quiz_id = data["daily_quiz_id"]
        option_id = data["quiz_answer_option_id"]

        # Validate quiz
        try:
            quiz = DailyQuiz.objects.get(id=quiz_id)
        except DailyQuiz.DoesNotExist:
            raise serializers.ValidationError({"daily_quiz_id": "Quiz not found."})

        # Validate option
        try:
            option = QuizAnswerOption.objects.get(id=option_id)
        except QuizAnswerOption.DoesNotExist:
            raise serializers.ValidationError({"quiz_answer_option_id": "Option not found."})

        # Option belongs to this quiz
        if option.daily_quiz_id != quiz.id:
            raise serializers.ValidationError({
                "quiz_answer_option_id": "This option does not belong to the selected quiz."
            })

        data["quiz"] = quiz
        data["option"] = option
        return data

    def create(self, validated_data):
        quiz = validated_data["quiz"]
        option = validated_data["option"]
        user_id = validated_data["user_id"]

        is_correct = option.is_correct
        points = 1 if is_correct else 0

        answer = QuizAnswer.objects.create(
            daily_quiz_id=quiz,
            quiz_answer_option_id=option,
            user_id_id=user_id,
            points=points
        )

        return {
            "correct": is_correct,
            "points": points
        }

