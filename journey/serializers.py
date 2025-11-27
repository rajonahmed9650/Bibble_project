from rest_framework import serializers
from .models import Journey,JourneyDetails,Journey_icon,Days





class JourneyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JourneyDetails
        fields = ["journey_id","image","details"]


class JourneyIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey_icon
        fields = ["journey_id","icon"]


class DaysSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    class Meta:
        model = Days
        fields = ["journey_id","name","image"]



class JourneySerilzers(serializers.ModelSerializer):
    days = DaysSerializer(many=True, read_only=True)
    icons = JourneyIconSerializer(many=True, read_only=True)
    details = JourneyDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = Journey
        fields = ["id", "name", "days", "icons", "details"]


