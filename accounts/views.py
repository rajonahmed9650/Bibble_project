from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password , check_password
from payments.models import Subscription,Package
from .models import User , Social_login ,OTP
from .serializers import*
from django.db.models import Q
from accounts.authentication import CustomJWTAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
import jwt as pyjwt

from .utils.utils import generate_otp_code ,save_session,create_jwt_token_for_user,save_otp_cache,delete_otp_cache,get_otp_cache,send_otp_code
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import time
from .models import Sessions,User


@method_decorator(csrf_exempt, name="dispatch")
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        ser = SignupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # CREATE USER
        user = User.objects.create_user(
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            password=data["password"]
        )
     

        # ✅ CREATE SOCIAL LOGIN ENTRY (IMPORTANT!)
        Social_login.objects.create(
            user=user,
            provider="email",
            provider_id=user.email,
            password=make_password(data["password"])   # hashed password
        )

        # CREATE SUBSCRIPTION (FREE PLAN)
        subscription = Subscription.objects.create(
            user=user,
            package=Package.objects.filter(package_name="free").first(),
            current_plan="free",
            expired_at=timezone.now() + timedelta(minutes =  10080),
            is_active=True
        )

        # CREATE TOKEN
        token, expire = create_jwt_token_for_user(user.id)
        save_session(user, token, expire)

        # WAIT 1 SECOND → ALLOW FRONTEND TO CONNECT WS
        return Response({
            "user_id": user.id,
            "message": "Signup completed successfully.",
            "subscription": {
                "user_id": subscription.user.id,
                "plan": subscription.current_plan,
                "expired_at": subscription.expired_at,
                "is_active": subscription.is_active
            },
            "token": token
        }, status=201)



class ProfileView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class OTPVerifiyView(APIView):
    def post(self, request):
        ser = OTPVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"]
        otp_input = data["otp"]

        saved_otp = get_otp_cache(email + "_otp")
        otp_type = get_otp_cache(email + "_type")

        if not saved_otp:

            return Response({"error": "OTP expired"}, status=400)

        if saved_otp != otp_input:

            return Response({"error": "Invalid OTP"}, status=400)


        # REMOVE OTP
        delete_otp_cache(email + "_otp")
        delete_otp_cache(email + "_type")

        # 1) REGISTER FLOW
        if otp_type == "register":
            temp_data = get_otp_cache(email + "_signup")
            if not temp_data:
                return Response({"error": "Signup session expired"}, status=400)

            user = User.objects.create_user(
                username=temp_data["username"],
                email=temp_data["email"],
                phone=temp_data["phone"],
                password=temp_data["password"]
            )

            Social_login.objects.create(
                user=user,
                provider="email",
                provider_id=email,
                password=make_password(temp_data["password"])
            )

            delete_otp_cache(email + "_signup")

            token, expire = create_jwt_token_for_user(user.id)
            save_session(user, token, expire)

            return Response({
                "message": "User verified successfully",
                "verify_status": "verified",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone
                }
            })

     
        if otp_type == "forgot_password":

           
            save_otp_cache(email + "_reset_allowed", True)
 

            return Response({
                "status": "verified",
                "message": "You can reset your password now.",
                "action": "reset_password"
            })

        
        if otp_type == "login_otp":
            user = User.objects.filter(email=email).first()
            token, expire = create_jwt_token_for_user(user.id)
            save_session(user, token, expire)

            return Response({"status": "login_success", "token": token})

        return Response({"error": "Invalid flow"}, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

      
        # GOOGLE LOGIN

        if data.get("google_token"):
            try:
                idinfo = google_id_token.verify_oauth2_token(
                    data["google_token"], google_requests.Request()
                )
                email = idinfo.get("email")
                google_uid = idinfo["sub"]
            except Exception as e:
                return Response({"error": "Invalid Google token"}, status=400)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]}
            )

            Social_login.objects.update_or_create(
                user=user,
                defaults={"provider": "google", "provider_id": google_uid}
            )

            token, expire = create_jwt_token_for_user(user.id)
            save_session(user, token, expire)

   

            return Response({
                "status": "success",
                "login_by": "google",
                "token": token,
                "plan_selection_needed": True,
                "category": user.category
            })

      
        # APPLE LOGIN
    
        if data.get("apple_token"):
            try:
                decoded = pyjwt.decode(data["apple_token"], options={"verify_signature": True})
                email = decoded.get("email")
                apple_uid = decoded["sub"]
            except Exception:
                return Response({"error": "Invalid Apple token"}, status=400)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]}
            )

            Social_login.objects.update_or_create(
                user=user,
                defaults={"provider": "apple", "provider_id": apple_uid}
            )

            token, expire = create_jwt_token_for_user(user.id)
            save_session(user, token, expire)

            return Response({
                "status": "success",
                "login_by": "apple",
                "token": token,
                "plan_selection_needed": True,
                "category": user.category
            })


        # EMAIL/PASSWORD LOGIN
      
        login_id = data.get("login_id")
        password = data.get("password")

        if login_id and password:
            try:
                user = User.objects.get(
                    Q(email=login_id) |
                    Q(phone=login_id) |
                    Q(username=login_id)
                )
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=400)
            if not user.is_active:
                return Response({"error": "Account disabled"}, status=403)
            social = Social_login.objects.filter(user=user, provider="email").first()
            if not social:
                return Response({"error": "Password login not allowed"}, status=400)

            if not check_password(password, social.password):
                return Response({"error": "Wrong password"}, status=400)

            token, expire = create_jwt_token_for_user(user.id)
            save_session(user, token, expire)

            has_active_plan = Subscription.objects.filter(
                user=user,
                is_active=True,
                expired_at__gt=timezone.now()
            ).exists()

            return Response({
                "status": "success",
                "login_by": "email",
                "token": token,
                "plan_selection_needed":  has_active_plan,
                "trial_expired": (
                    "Your subscription has expired. Please renew your plan."
                    if not has_active_plan
                    else "Subscription active"
                 ),
                "category": user.category
            })

        return Response({"error": "Invalid request"}, status=400)

class ResetPasswordView(APIView):
    def post(self, request):
        ser = ResetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"]
        new_password = data["new_password"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=400)

        # Check if OTP verify happened
        allowed = get_otp_cache(email + "_reset_allowed")
        if not allowed:
            return Response({"error": "OTP not verified"}, status=400)

        social = Social_login.objects.filter(user=user, provider="email").first()
        if not social:
            return Response({"error": "Not an email account"}, status=400)

        social.password = make_password(new_password)
        social.save()

        delete_otp_cache(email + "_reset_allowed")




        return Response({
            "message": "Password reset successfully."
        })
  
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication

class ForgotPasswordView(APIView):
     # disable JWT + Basic + Session
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        ser = ForgotPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"error": "User not found"}, status=400)

        otp = generate_otp_code()

        save_otp_cache(email + "_otp", otp)
        save_otp_cache(email + "_type", "forgot_password")

        send_otp_code(email, otp)

        return Response({
            "status": "otp_sent",
            "email": email
        })



        
class ChangePasswordView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        old_password = data["old_password"]
        new_password = data["new_password"]

        user = request.user  # Logged-in user
        identity = Social_login.objects.filter(user=user, provider="email").first()

        if not identity:
            return Response({"error": "Password change allowed only for email users"}, status=400)

        if not check_password(old_password, identity.password):
            return Response({"error": "Old password is incorrect"}, status=400)

        identity.password = make_password(new_password)
        identity.save()




        return Response({"status": "password_changed"})
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) Read email from POST body
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        # 2) Check if email belongs to logged-in user
        if request.user.email != email:
            return Response({"error": "Email does not match logged-in user"}, status=400)

        # 3) Find token (JWT)
        token = request.auth  

        if not token:
            return Response({"error": "No active token found"}, status=400)

        # 4) Delete session by token
        Sessions.objects.filter(token=token).delete()

        return Response({
            "status": "logged_out",
            "email": email
        }, status=200)


import requests
from journey.models import PersonaJourney, Journey, Days
from userprogress.models import UserJourneyProgress, UserDayProgress

from django.db import transaction


class CategorizeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        qa_pairs = request.data.get("qa_pairs")

        if not qa_pairs:
            return Response({"error": "qa_pairs is required"}, status=400)

        if user.category:
            return Response({"message": "Category already assigned"}, status=200)

        # 🔹 External categorization
        response = requests.post(
            "http://206.162.244.131:8001/api/categorize/",
            json={"qa_pairs": qa_pairs},
            timeout=10
        )
        data = response.json()

        category = data.get("category")
        if not category:
            return Response({"error": "No category returned"}, status=502)

        user.category = category
        user.save()

        # =================================================
        # 🔥 CRITICAL FIX: CLEAN OLD JOURNEYS
        # =================================================
        UserJourneyProgress.objects.filter(
            user=user
        ).update(status="locked")

        persona = PersonaJourney.objects.filter(
            persona=category
        ).first()

        if not persona or not persona.sequence:
            return Response({"error": "Persona sequence not configured"}, status=500)

        # 1️⃣ FIRST JOURNEY (sequence[0])
        first_journey = Journey.objects.get(id=persona.sequence[0])

        UserJourneyProgress.objects.update_or_create(
            user=user,
            journey=first_journey,
            defaults={
                "status": "current",
                "completed": False,
                "completed_days": 0
            }
        )

        # 2️⃣ FIRST DAY
        first_day = Days.objects.filter(
            journey_id=first_journey,
            order=1
        ).first()

        if first_day:
            UserDayProgress.objects.update_or_create(
                user=user,
                day_id=first_day,
                defaults={"status": "current"}
            )

        return Response(
            {
                "message": "Category saved successfully",
                "category": category
            },
            status=200
        )


from django.contrib.auth import authenticate


class DisableAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        active = request.data.get("active")

        # Accept both true and "true"
        if str(active).lower() != "true":
            return Response(
                {"error": "active=true is required to disable account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Disable account
        user.is_active = False
        user.save()

        # Remove all active sessions (important)
        Sessions.objects.filter(user=user).delete()

        return Response(
            {"message": "Account disabled successfully"},
            status=status.HTTP_200_OK
        )

