import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Subscription
from .serializers import CreateSubscriptionSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime



stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan = request.data.get("plan")
        user = request.user

        if plan == "monthly":
            price = settings.STRIPE_MONTHLY_PRICE
        elif plan == "yearly":
            price = settings.STRIPE_YEARLY_PRICE
        else:
            return Response({"error": "Invalid plan"}, 400)

        sub, _ = Subscription.objects.get_or_create(user=user)

        if not sub.stripe_customer_id:
            # Create Stripe customer
            customer = stripe.Customer.create(email=user.email)
            sub.stripe_customer_id = customer.id
            sub.save()

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=sub.stripe_customer_id,
            line_items=[{"price": price, "quantity": 1}],
            metadata={"user_id": user.id},
            success_url="https://yourdomain/success/",
            cancel_url="https://yourdomain/cancel/",
        )

        return Response({"checkout_url": session.url})



class StripeWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
        except:
            return Response({"error": "Invalid signature"}, 400)

        event_type = event["type"]
        data = event["data"]["object"]

        # CHECKOUT SUCCESS
        if event_type == "checkout.session.completed":
            customer_id = data["customer"]
            subscription_id = data["subscription"]

            sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
            if not sub:
                return Response({"status": "no-sub-found"})

            # Read price
            line_items = stripe.checkout.Session.list_line_items(data["id"])
            price_id = line_items["data"][0]["price"]["id"]

            if price_id == settings.STRIPE_MONTHLY_PRICE:
                sub.current_plan = "monthly"
            else:
                sub.current_plan = "yearly"

            sub.stripe_subscription_id = subscription_id
            sub.trial_end = None
            sub.is_active = True
            sub.save()

        return Response({"status": "ok"})


