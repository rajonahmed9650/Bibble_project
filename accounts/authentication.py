import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from accounts.models import User, Sessions


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):

        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None
        
        # Expect: "Bearer <token>"
        try:
            prefix, token = auth_header.split(" ")
        except:
            raise AuthenticationFailed("Invalid token header format")

        if prefix.lower() != "bearer":
            raise AuthenticationFailed("Token must start with Bearer")

        # Decode JWT token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        user = User.objects.filter(id=user_id).first()

        if not user:
            raise AuthenticationFailed("User not found")

        # Check session token exists in DB
        session_exists = Sessions.objects.filter(user=user, token=token).exists()
        if not session_exists:
            raise AuthenticationFailed("Session expired or invalid")

        # The token MUST be returned as second object (important for logout!)
        return (user, token)
