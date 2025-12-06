from .models import DailyDevotion,DailyPrayer,MicroAction,DailyReflectionSpace
from rest_framework import serializers



class DailyDevotionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyDevotion
        fields = ["id","journey_id","day_id","scripture_name","devotion","reflection"]

    def validate(self, data):
        scripture_name = data.get("scripture_name")
        if DailyDevotion.objects.filter(scripture_name=scripture_name).exists():
            raise serializers.ValidationError(
                {"Scripture_name":"This scripture already exists"}
            )
        return data

        

class DailyReflicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReflectionSpace
        fields = ["dailydevotion_id","reflection_note"]





class DailyPrayerSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = DailyPrayer
        fields = ["id", "journey_id", "day_id", "prayer", "audio_url"]

    def get_audio_url(self, obj):
        request = self.context.get("request", None)

        if obj.audio:
            if request:
                return request.build_absolute_uri(obj.audio.url)
            else:
                return obj.audio.url  # fallback
        return None

    def validate(self, data):
        prayer = data.get("prayer")
        if DailyPrayer.objects.filter(prayer=prayer).exists():
            raise serializers.ValidationError({"prayer": "This prayer already exists"})
        return data

   


class MicroActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroAction
        fields = ["id","journey_id","day_id","action"]

