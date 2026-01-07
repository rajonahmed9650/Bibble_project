import random
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from ..models import Sessions
import jwt

OTP_EXPIRY_MINUTES = 5
JWT_SECRET = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
JWT_ALGO = "HS256"


# =========================
# OTP UTILS
# =========================
def generate_otp_code():
    return f"{random.randint(100000, 999999)}"


def save_otp(email, otp, otp_type):
    """
    Save OTP + flow type in a single cache object
    """
    cache.set(
        f"otp_{email}",
        {
            "otp": otp,
            "type": otp_type,
            "created_at": timezone.now().isoformat(),
        },
        timeout=OTP_EXPIRY_MINUTES * 60,
    )
    cache.set(f"otp_attempt_{email}", 0, timeout=OTP_EXPIRY_MINUTES * 60)


def get_otp(email):
    return cache.get(f"otp_{email}")


def delete_otp(email):
    cache.delete(f"otp_{email}")
    cache.delete(f"otp_attempt_{email}")


def increase_otp_attempt(email):
    key = f"otp_attempt_{email}"
    attempts = cache.get(key, 0)
    cache.set(key, attempts + 1, timeout=OTP_EXPIRY_MINUTES * 60)
    return attempts + 1
  
def set_reset_allowed(email):
    cache.set(f"reset_allowed_{email}", True, timeout=300)


def is_reset_allowed(email):
    return cache.get(f"reset_allowed_{email}", False)


def clear_reset_allowed(email):
    cache.delete(f"reset_allowed_{email}")


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

Your one-time verification code is: {otp}

This code will expire in 5 minutes.

— Bible Journey Team
"""

    html_content = f"""
<html>
<body>
  <h2>Bible Journey Verification</h2>
  <p>Your verification code:</p>
  <h1>{otp}</h1>
  <p>This code will expire in 5 minutes.</p>
</body>
</html>
"""

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        f"Bible Journey <{settings.DEFAULT_FROM_EMAIL}>",
        [email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)



def save_session(user,token,expire):
    
    return Sessions.objects.create(user=user,token=token,expire_at=expire)