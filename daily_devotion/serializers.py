from .models import DailyDevotion,DailyPrayer,MicroAction
from rest_framework import serializers



class DailyDevotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyDevotion
        fields = ["id","journey_id","day_id","name","devotion","reflection"]


class DailyPrayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrayer
        fields = ["id","journey_id","day_id","name","prayer"]


class MicroActionSerializer(serializers.ModelSerializer):
    class Meta:
        Model = MicroAction
        fields = ["id","journey_id","day_id","action"]

