from rest_framework import serializers

class CreateSubscriptionSerializer(serializers.Serializer):
    # allowed: "trial", "monthly", "yearly"
    plan = serializers.ChoiceField(choices=["trial", "monthly", "yearly"])



