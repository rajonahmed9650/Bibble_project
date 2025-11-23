from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password , check_password
from .models import User , Social_login ,OTP
from .serializers import*
from django.db.models import Q
from accounts.authentication import CustomJWTAuthentication
from rest_framework.permissions import IsAuthenticated

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
import jwt as pyjwt

from .utils import generate_otp_code ,save_session,create_jwt_token_for_user,save_otp_cache,delete_otp_cache,get_otp_cache,send_otp_code





class SignupView(APIView):
    def post(self, request):
        ser = SignupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"]
        phone = data["phone"]
        username = data["username"]
        password = data["password"]

        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=400)
        if User.objects.filter(phone=phone).exists():
            return Response({"error": "Phone already exists"}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

      
        temp_user_data = {
            "username": username,
            "email": email,
            "phone": phone,
            "password": password
        }
        save_otp_cache(email + "_signup", temp_user_data)

    
        otp = generate_otp_code()
        save_otp_cache(email + "_otp", otp)

     
        save_otp_cache(email + "_type", "register")   

       
        send_otp_code(email, otp)

        return Response({"status": "otp_sent"})




# class OTPRequestView(APIView):
#     def post(self,request):
#         ser = OTPRequestSerializer(data =request.data)
#         ser.is_valid(raise_exception=True)
#         data = ser.validated_data
#         email = data.get("email")
#         otp_type = data.get("type")

#         if not email:
#             return Response({"error":"Email required"},status=status.HTTP_400_BAD_REQUEST)
#         user = User.objects.filter(email=email).first()
#         if not user:
#             return Response({"error":"User not found"},status=status.HTTP_400_BAD_REQUEST)
        

#         if otp_type == "forgot_password":
#             social = getattr(user,"social_login",None)
#             if not social or social.provider != "email":
#                 return Response({"error":"Password reset only for email users"},status=status.HTTP_400_BAD_REQUEST)
            
#             otp = generate_otp_code()

#             save_otp_cache(email,otp)

#             send_otp_code(email,otp)
            
#             return Response({
#                 "status":"opt_sent",
#                 "otp":otp
#             })
        

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
    def post(self, request):

        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # -----------------------------------------
        # GOOGLE LOGIN
        # -----------------------------------------
        # if data.get("google_token"):
        #     token = data["google_token"]
        #     try:
        #         idinfo = google_id_token.verify_oauth2_token(
        #             token, google_requests.Request()
        #         )
        #         sub = idinfo["sub"]
        #     except Exception as e:
        #         return Response({"error": "Invalid Google token", "details": str(e)}, status=400)

        #     social = Social_login.objects.filter(provider="google", provider_id=sub).first()
        #     if not social:
        #         return Response({"error": "Google user not registered"}, status=400)

        #     user = social.user
        #     token_jwt, expire = create_jwt_token_for_user(user.id)
        #     save_session(user, token_jwt, expire)
        #     return Response({"token": token_jwt})
        if data.get("google_token"):
            token = data["google_token"]
            try:
                idinfo = google_id_token.verify_oauth2_token(
                    token, google_requests.Request()
                )
                email = idinfo.get("email")
                sub = idinfo["sub"]   # Google unique ID
            except Exception as e:
                return Response({"error": "Invalid Google token", "details": str(e)}, status=400)

    # AUTO CREATE USER IF NOT EXISTS
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]}
            )

    # AUTO CREATE / UPDATE SOCIAL LOGIN RECORD
            social, _ = Social_login.objects.update_or_create(
                user=user,
                defaults={
                    "provider": "google",
                    "provider_id": sub
                }
            )

    # AUTO LOGIN (Generate Token)
            token_jwt, expire = create_jwt_token_for_user(user.id)
            save_session(user, token_jwt, expire)

            return Response({
                "status": "success",
                "action": "google_login",
                "auto_signup": created,   # True হলে user নতুন তৈরি হয়েছে
                "token": token_jwt
            })
        


        # -----------------------------------------
        # APPLE LOGIN
        # -----------------------------------------
        # if data.get("apple_token"):
        #     token = data["apple_token"]
        #     try:
        #         decode = pyjwt.decode(token, options={"verify_signature": False})
        #         sub = decode["sub"]
        #     except Exception as e:
        #         return Response({"error": "Invalid Apple token", "details": str(e)}, status=400)

        #     social = Social_login.objects.filter(provider="apple", provider_id=sub).first()
        #     if not social:
        #         return Response({"error": "Apple user not registered"}, status=400)

        #     user = social.user
        #     token_jwt, expire = create_jwt_token_for_user(user.id)
        #     save_session(user, token_jwt, expire)
        #     return Response({"token": token_jwt})
        


        if data.get("apple_token"):
            token = data["apple_token"]
            try:
                decode = pyjwt.decode(token, options={"verify_signature": True})
                email = decode.get("email")
                sub = decode["sub"]   # Apple unique user ID
            except Exception as e:
                return Response({"error": "Invalid Apple token", "details": str(e)}, status=400)

    # AUTO CREATE USER IF NOT EXISTS
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0]}
            )

    # AUTO CREATE OR UPDATE SOCIAL LOGIN RECORD
            social, _ = Social_login.objects.update_or_create(
                user=user,
                defaults={
                    "provider": "apple",
                    "provider_id": sub
                }
            )

    # LOGIN TOKEN
            token_jwt, expire = create_jwt_token_for_user(user.id)
            save_session(user, token_jwt, expire)

            return Response({
                "status": "success",
                "action": "apple_login",
                "auto_signup": created,    # TRUE হলে নতুন user তৈরি হয়েছে
                "token": token_jwt
            })

        # -----------------------------------------
        # OTP LOGIN
        # -----------------------------------------
        if data.get("otp") and data.get("login_id"):
            email = data["login_id"]
            otp = data["otp"]

            saved_otp = get_otp_cache(email)
            if not saved_otp:
                return Response({"error": "OTP expired"}, status=400)

            if saved_otp != otp:
                return Response({"error": "Invalid OTP"}, status=400)

            delete_otp_cache(email)

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found"}, status=400)

            token_jwt, expire = create_jwt_token_for_user(user.id)
            save_session(user, token_jwt, expire)
            return Response({"token": token_jwt})


        # -----------------------------------------
        # EMAIL / PHONE / USERNAME LOGIN (PASSWORD)
        # -----------------------------------------
        login_id = data.get("login_id")
        password = data.get("password")

        if login_id and password:
            # find user by username OR email OR phone
            try:
                user = User.objects.get(
                    Q(email=login_id) |
                    Q(phone=login_id) |
                    Q(username=login_id)
                )
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=400)

            social = Social_login.objects.filter(user=user, provider="email").first()
            if not social:
                return Response({"error": "This user cannot login via password"}, status=400)

            if not check_password(password, social.password):
                return Response({"error": "Wrong password"}, status=400)

            token_jwt, expire = create_jwt_token_for_user(user.id)
            save_session(user, token_jwt, expire)
            return Response({"token": token_jwt})


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
            "status": "password_reset_success",
            "message": "Password reset successfully."
        })
  
                



class ForgotPasswordView(APIView):
    def post(self, request):
        ser = ForgotPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        email = data["email"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=400)

        otp = generate_otp_code()

        save_otp_cache(email + "_otp", otp)
        save_otp_cache(email + "_type", "forgot_password")

        send_otp_code(email, otp)

        return Response({
            "status": "otp_sent",
            "message": "OTP sent to your email.",
            "email": email
        })


    

# class ResetPasswordView(APIView):
#     def post(self, request):
#         ser = ResetPasswordSerializer(data=request.data)
#         ser.is_valid(raise_exception=True)
#         data = ser.validated_data

#         email = data["email"]
#         new_password = data["new_password"]

#         user = User.objects.filter(email=email).first()
#         if not user:
#             return Response({"error": "User not found"}, status=400)

#         identity = Social_login.objects.filter(user=user, provider="email").first()
#         identity.password = make_password(new_password)
#         identity.save()

#         return Response({"status": "password_reset_success"})    



# class ResetPasswordView(APIView):
#     def post(self,request):
#         ser = ResetPasswordSerializer(data = request.data)
#         ser.is_valid(raise_exception=True)
#         data = ser.validated_data

#         email = data["email"]
#         new_password = data["new_password"]

#         user = User.objects.filter(email=email).first()
#         if not user:
#             return Response({"error":"User not found"},status=status.HTTP_400_BAD_REQUEST)
        
#         identity = Social_login.objects.filter(user=user,provider = "email").first()
#         identity.password = make_password(new_password)
#         identity.save()

#         return Response({"status":"Passowrd reset success"})
    
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