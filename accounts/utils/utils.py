import random
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from ..models import Sessions
from django.core.mail import EmailMultiAlternatives
import jwt

OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5

JWT_SECRET = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
JWT_ALGO = "HS256"


# =========================
# OTP GENERATE
# =========================
def generate_otp_code():
    return f"{random.randint(100000, 999999)}"


# =========================
# OTP SAVE
# =========================
def save_otp(email, otp, otp_type):
    cache.set(
        f"otp_{email}",
        {
            "otp": otp,
            "type": otp_type,
            "created_at": timezone.now().timestamp(),
        },
        timeout=OTP_EXPIRY_MINUTES * 60,
    )
    cache.set(
        f"otp_attempt_{email}",
        0,
        timeout=OTP_EXPIRY_MINUTES * 60,
    )


# =========================
# OTP VERIFY
# =========================
def verify_otp(email, otp, otp_type):
    data = cache.get(f"otp_{email}")

    if not data:
        return False, "OTP expired"

    #  expiry check
    if timezone.now().timestamp() - data["created_at"] > OTP_EXPIRY_MINUTES * 60:
        delete_otp(email)
        return False, "OTP expired"

    #  attempt check
    attempts = cache.get(f"otp_attempt_{email}", 0)
    if attempts >= MAX_OTP_ATTEMPTS:
        delete_otp(email)
        return False, "Too many attempts"

    #  invalid otp
    if data["otp"] != otp or data["type"] != otp_type:
        cache.incr(f"otp_attempt_{email}")
        return False, "Invalid OTP"

    #  success
    delete_otp(email)
    set_reset_allowed(email)
    return True, "OTP verified"


def delete_otp(email):
    cache.delete(f"otp_{email}")
    cache.delete(f"otp_attempt_{email}")


# =========================
# RESET FLAG
# =========================
def set_reset_allowed(email):
    cache.set(f"reset_allowed_{email}", True, timeout=300)


def is_reset_allowed(email):
    return cache.get(f"reset_allowed_{email}", False)


def clear_reset_allowed(email):
    cache.delete(f"reset_allowed_{email}")


# =========================
# EMAIL SEND
# =========================
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


# =========================
# JWT (UNCHANGED)
# =========================
def create_jwt_token_for_user(user_id, days_valid=3):
    expire = timezone.now() + timedelta(minutes=days_valid)

    payload = {
        "user_id": user_id,
        "exp": int(expire.timestamp()),
        "iat": int(timezone.now().timestamp()),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token, expire

def save_session(user,token,expire): 
    return Sessions.objects.create(user=user,token=token,expire_at=expire)