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

# def send_otp_code(email,otp):
#     subject = "Your Otp code"
#     message = f"Your OTP is: {otp}\n It will expire in 5 minutes."

#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,
#         [email],
#         fail_silently=False
#     )


from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_otp_code(email, otp):
    subject = "Bible Journey – Your Verification Code"

    text_content = f"""
Hi,

Your one-time verification code for Bible Journey is:

{otp}

This code will expire in 5 minutes.

If you didn’t request this, you can safely ignore this email.

— Bible Journey Team

"""

    html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2>Bible Journey Verification</h2>
    <p>Your one-time verification code is:</p>
    <h1 style="letter-spacing: 2px;">{otp}</h1>
    <p>This code will expire in <strong>5 minutes</strong>.</p>
    <p>If you didn’t request this, please ignore this email.</p>
    <br>
    <p>— Bible Journey Team</p>
  </body>
</html>
"""

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=f"Bible Journey <{settings.DEFAULT_FROM_EMAIL}>",
        to=[email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)



def save_session(user,token,expire):
    
    return Sessions.objects.create(user=user,token=token,expire_at=expire)