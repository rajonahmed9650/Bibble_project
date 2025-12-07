import random
from datetime import timedelta
from django.utils import timezone
import jwt
from django.core.cache import cache
from django.conf import settings
from ..models import Sessions
from django.core.mail import  send_mail

JWT_SECRET = getattr(settings,"JWT_SECRET",settings.SECRET_KEY)
JWT_ALGO = "HS256"

OTP_EXPIRY_MINUTES = 5  

def generate_otp_code():
    return f"{random.randint(100000,999999):06d}"

def save_otp_cache(email,otp):
    cache.set(f"otp_{email}",otp,timeout=OTP_EXPIRY_MINUTES*60)

def get_otp_cache(email):
    return cache.get(f"otp_{email}")

def delete_otp_cache(email):
    cache.delete(f"otp_{email}")    


def create_jwt_token_for_user(user_id,days_vaild=7):
    expire = timezone.now() + timedelta(days=days_vaild)

    payload = {
        "user_id" : user_id,
        "exp": int(expire.timestamp()),
        "iat": int(timezone.now().timestamp())
    }

    token = jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGO)

    return token,expire

def send_otp_code(email,otp):
    subject = "Your Otp code"
    message = f"Your OTP is: {otp}\n It will expire in 5 minutes."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )


def save_session(user,token,expire):
    
    return Sessions.objects.create(user=user,token=token,expire_at=expire)