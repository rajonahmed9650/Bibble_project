from rest_framework import serializers
from .models import User,Profile
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password"]
        extra_kwargs = {
            "username": {"validators": []},  # REMOVE UNIQUE VALIDATION
        }    

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone already exists")
        return value

    # def validate_username(self, value):
    #     if User.objects.filter(username=value).exists():
    #         raise serializers.ValidationError("Username already exists")
    #     return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            password=validated_data["password"]
        )
        return user   
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["name","email","phone","gender","date_of_birth","avatar"]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class LoginSerializer(serializers.Serializer):
    login_id = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True)

    google_token = serializers.CharField(required=False, allow_null=True)
    apple_token = serializers.CharField(required=False, allow_null=True)

    otp = serializers.CharField(required=False, allow_null=True)

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("New password and confirm password do not match")
        return data
