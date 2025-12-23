from rest_framework import serializers
from .models import jourenystepitem

class JourneyStepItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = jourenystepitem
        fields = [
            "id",
            "journey_id",
            "days_id",
            "step_name",      
        ]
