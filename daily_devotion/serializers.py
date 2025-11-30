from .models import DailyDevotion,DailyPrayer,MicroAction
from rest_framework import serializers



class DailyDevotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyDevotion
        fields = ["id","journey_id","day_id","name","devotion","reflection"]


class DailyPrayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPrayer
        fields = ["id","journey_id","day_id","prayer","audio"]
    def get_audio(self, obj):
        request = self.context.get("request")

        if obj.audio:
            return request.build_absolute_uri(obj.audio.url)
        return None    


class MicroActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroAction
        fields = ["id","journey_id","day_id","action"]

