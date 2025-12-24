from rest_framework import serializers

class CreateSubscriptionSerializer(serializers.Serializer):
    # FRONTEND MUST SEND THIS
    package_id = serializers.IntegerField()

    # Only allow valid billing choices
    plan = serializers.ChoiceField(choices=["free","weekly","monthly", "yearly"])



