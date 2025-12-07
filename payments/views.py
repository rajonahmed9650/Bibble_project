# payments/views.py

import stripe
from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Subscription
from notifications.utils import push_notification
from accounts.utils.messages import SYSTEM_MESSAGES

from datetime import datetime, timedelta, timezone as dt_timezone   


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan = request.data.get("plan")

        # 1️ VALIDATE PLAN
        if plan == "monthly":
            price = settings.STRIPE_MONTHLY_PRICE
        elif plan == "yearly":
            price = settings.STRIPE_YEARLY_PRICE
        else:
            return Response({"error": "Invalid plan"}, status=400)

        # 2️ GET OR CREATE SUBSCRIPTION
        sub, created = Subscription.objects.get_or_create(user=user)

        # 3 BLOCK IF NOT EXPIRED
        if sub.billing_period_end and sub.billing_period_end > timezone.now():
            push_notification(user.id, {
                "title": "Subscription Active",
                "message": SYSTEM_MESSAGES["subscription_blocked"]
                           + str(sub.billing_period_end)
            })

            return Response({
                "error": "Active subscription exists",
                "expires_on": sub.billing_period_end,
                "can_renew": False
            }, status=403)

        # 4️ CREATE STRIPE CUSTOMER
        if not sub.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            sub.stripe_customer_id = customer.id
            sub.save()

        # 5️ CREATE CHECKOUT SESSION
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=sub.stripe_customer_id,
            line_items=[{"price": price, "quantity": 1}],
            metadata={"user_id": user.id, "plan": plan},
            success_url="http://127.0.0.1:8000/",
            cancel_url="http://127.0.0.1:8000/",
        )

        return Response({
            "checkout_url": session.url,
            "can_renew": True
        })


class StripeWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = []   # must disable DRF parser

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, secret
            )
        except Exception:
            return Response({"error": "Invalid Stripe signature"}, status=400)

        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})

        # ========================================================
        # 1PAYMENT SUCCESS
        # ========================================================
        if event_type == "checkout.session.completed":
            customer_id = data.get("customer")
            subscription_id = data.get("subscription")

            sub = Subscription.objects.filter(
                stripe_customer_id=customer_id
            ).first()

            if not sub:
                return Response({"status": "subscription-not-found"}, status=200)

            # fallback if Stripe doesn't send subscription id
            if not subscription_id:
                subs = stripe.Subscription.list(customer=customer_id, limit=1)
                if subs.data:
                    subscription_id = subs.data[0].id

            stripe_sub = stripe.Subscription.retrieve(subscription_id)

            # PLAN DETECT
            price_id = None
            items = stripe_sub.get("items", {}).get("data", [])
            if items:
                price_id = items[0]["price"]["id"]

            if price_id == settings.STRIPE_MONTHLY_PRICE:
                sub.current_plan = "monthly"
            elif price_id == settings.STRIPE_YEARLY_PRICE:
                sub.current_plan = "yearly"
            else:
                sub.current_plan = "monthly"

            # PERIOD DETECT (safe)
            current_period_end = getattr(stripe_sub, "current_period_end", None)
            if not current_period_end:
                current_period_end = getattr(
                    stripe_sub, "billing_cycle_anchor", None
                )

            if current_period_end:
                sub.billing_period_end = datetime.fromtimestamp(
                    current_period_end,
                    tz=dt_timezone.utc    
                )
            else:
                sub.billing_period_end = timezone.now() + timedelta(days=30)

            sub.is_active = True
            sub.stripe_subscription_id = subscription_id
            sub.save()

            push_notification(sub.user.id, {
                "title": "Subscription Started",
                "message": f"Active until {sub.billing_period_end}"
            })

            return Response({"status": "subscription-activated"}, status=200)

        # ========================================================
        # 2️PAYMENT FAILED
        # ========================================================
        if event_type == "invoice.payment_failed":
            subscription_id = data.get("subscription")
            sub = Subscription.objects.filter(
                stripe_subscription_id=subscription_id
            ).first()

            if sub:
                sub.is_active = False
                sub.save()

                push_notification(sub.user.id, {
                    "title": "Payment Failed",
                    "message": SYSTEM_MESSAGES["payment_failed"]
                })

        # ========================================================
        # 3️ SUBSCRIPTION CANCELLED
        # ========================================================
        if event_type == "customer.subscription.deleted":
            subscription_id = data.get("id")
            sub = Subscription.objects.filter(
                stripe_subscription_id=subscription_id
            ).first()

            if sub:
                sub.current_plan = "none"
                sub.is_active = False
                sub.billing_period_end = None
                sub.save()

                push_notification(sub.user.id, {
                    "title": "Subscription Cancelled",
                    "message": SYSTEM_MESSAGES["subscription_cancelled"]
                })

        return Response({"status": "ok"}, status=200)
