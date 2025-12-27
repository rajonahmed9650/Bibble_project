from rest_framework import serializers
from .models import Journey,JourneyDetails,Journey_icon,Days

class JourneyDetailsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = JourneyDetails
        fields = ["journey_id", "details", "image"]



class JourneyIconSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(required=False)

    class Meta:
        model = Journey_icon
        fields = ["journey_id", "icon"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        
        if instance.icon and hasattr(instance.icon, "url"):
            if request:
                rep["icon"] = request.build_absolute_uri(instance.icon.url)
            else:
                rep["icon"] = instance.icon.url
        
        return rep



class DaysSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Days
        fields = ["id", "journey_id", "name", "order", "image", "image_url"]
        extra_kwargs = {
            "image": {"write_only": True}  # upload only
        }

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None







class JourneySerilzers(serializers.ModelSerializer):
    
    icons = JourneyIconSerializer(many=True, read_only=True)
    details = JourneyDetailsSerializer(many = True , read_only = True)

    class Meta:
        model = Journey
        fields = ["id", "name","icons","details"]
    def validate_name(self, value):
        if Journey.objects.filter(name=value).exists():
            raise serializers.ValidationError("This Jouney  already exists.")
        return value


from userprogress.models import UserJourneyProgress




from rest_framework import serializers
from journey.models import Journey
from userprogress.models import UserJourneyProgress


class JourneyWithStatusSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    completed_days = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = ["id", "name", "status", "completed_days"]

    def get_status(self, obj):
        user = self.context["request"].user
        progress = UserJourneyProgress.objects.filter(
            user=user,
            journey=obj
        ).first()
        return progress.status if progress else "locked"

    def get_completed_days(self, obj):
        user = self.context["request"].user
        progress = UserJourneyProgress.objects.filter(
            user=user,
            journey=obj
        ).first()
        return progress.completed_days if progress else 0
