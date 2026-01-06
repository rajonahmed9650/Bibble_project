from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, phone=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, phone, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True,null=True,blank=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255,blank=True,null=True)
    last_category = models.CharField(max_length=50, null=True, blank=True)

    journey_start_date = models.DateField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    # def save(self, *args, **kwargs):
    #     if not self.username and self.full_name:
    #         base_username = self.full_name.lower().replace(" ", "_")
    #         new_username = base_username
    #         counter = 1

    #     # Ensure unique username
    #         while User.objects.filter(username=new_username).exists():
    #             new_username = f"{base_username}_{counter}"
    #             counter += 1

    #         self.username = new_username

    #     super().save(*args, **kwargs)


    def __str__(self):
         return f"{self.email}-{self.id}"



class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    avatar = models.ImageField(upload_to="avatars/",blank=True,null=True)  
    gender = models.CharField(
        max_length=12,
        choices=[
            ("male","Male"),
            ("female","Female"),
            ("other","Other"),
        ],
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True,null=True)

    def __str__(self):
        return f"{self.user.email} profile"


    

class Social_login(models.Model):
    PROVIDER_CHOICES =(
        ("email","Email"),
        ("google","Google"),
        ("apple","Apple"),
    )

    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='user_identity')
    provider = models.CharField(max_length=20,choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=255,null=True,blank=True)
    password = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} ({self.provider})"
    


class OTP(models.Model):
    OTP_TYPES = (
        ("register", "Register"),
        ("forgot_password", "Forgot Password"),
        ("login_otp", "Login OTP"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    type = models.CharField(max_length=30, choices=OTP_TYPES)
    expire_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "type", "code"]),
        ]

    def is_valid(self):
        return timezone.now() <= self.expire_at

    def __str__(self):
        return f"OTP {self.code} ({self.type}) for {self.user.email}"


class Sessions(models.Model):
    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="sessions")
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()

    def __str__(self):
        return f"Session {self.session_id} for {self.user}"      