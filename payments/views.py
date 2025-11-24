from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Subscription
from .serializers import CreateSubscriptionSerializer
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data["plan"]   # monthly / yearly
        user = request.user

        # Get price ID from environment
        if plan == "monthly":
            price_id = settings.STRIPE_MONTHLY_PRICE
        elif plan == "yearly":
            price_id = settings.STRIPE_YEARLY_PRICE
        else:
            return Response({"error": "Invalid plan"}, status=400)

        # Get or create subscription object
        sub, created = Subscription.objects.get_or_create(user=user)

        # Create stripe customer if not exists
        if not sub.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            sub.stripe_customer_id = customer.id
            sub.save()

        # Create checkout session
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=sub.stripe_customer_id,
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            success_url="http://127.0.0.1:8000/payments/success/",  # Change for mobile app
            cancel_url="http://127.0.0.1:8000/payments/cancel/",
        )

        return Response({
            "checkout_url": session.url,
            "session_id": session.id
        })