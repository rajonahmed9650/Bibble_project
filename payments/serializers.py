from .models import Subscription
from rest_framework import serializers

class CreateSubscriptionSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=["monthly", "yearly"])


