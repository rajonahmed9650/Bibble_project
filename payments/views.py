import stripe
from datetime import timedelta, datetime
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Subscription, Package


stripe.api_key = settings.STRIPE_SECRET_KEY


# =========================
#  CHECKOUT SESSION
# =========================
class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan = request.data.get("plan")        # "monthly" or "yearly"
        package_id = request.data.get("package_id")

        # get package
        pkg = Package.objects.filter(id=package_id).first()
        if not pkg:
            return Response({"error": "Invalid package"}, status=400)

        # select stripe price id
        if plan == "monthly":
            price_id = pkg.stripe_monthly_price_id
        elif plan == "yearly":
            price_id = pkg.stripe_yearly_price_id
        else:
            return Response({"error": "Invalid plan"}, status=400)

        # subscription row
        sub, created = Subscription.objects.get_or_create(user=user)

        # create stripe customer only if needed
        if not sub.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            sub.stripe_customer_id = customer.id
            sub.save()

        # create checkout
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=sub.stripe_customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "user_id": user.id,
                "package_id": pkg.id,
                "plan": plan
            },
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/",
        )

        return Response({"checkout_url": session.url}, status=200)


# =========================
#  STRIPE WEBHOOK
# =========================
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = []

    def post(self, request):
        payload = request.body
        sig = request.META.get("HTTP_STRIPE_SIGNATURE")
        secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig, secret)
        except Exception:
            return Response({"error": "invalid signature"}, status=400)

        data = event["data"]["object"]
        event_type = event["type"]

        

        # ===================================
        # CHECKOUT COMPLETED (FIRST PAYMENT)
        # ===================================
        if event_type == "checkout.session.completed":
            customer_id = data.get("customer")
            subscription_id = data.get("subscription")

            sub = Subscription.objects.filter(
                stripe_customer_id=customer_id
            ).first()

            if not sub:
                return Response({"status": "no-local-subscription"}, status=200)

            plan = data.get("metadata", {}).get("plan")
            pkg_id = data.get("metadata", {}).get("package_id")
            pkg = Package.objects.get(id=pkg_id)

            now = timezone.now()

            # manual expiry logic
            if plan == "monthly":
                sub.expired_at = now + timedelta(days=30)
            elif plan == "yearly":
                sub.expired_at = now + timedelta(days=365)

            sub.package = pkg
            sub.current_plan = plan
            sub.stripe_subscription_id = subscription_id
            sub.is_active = True
            sub.save()

            return Response({"status": "premium-activated"}, status=200)

        # ===================================
        # RECURRING PAYMENT SUCCESS
        # ===================================
        if event_type == "invoice.payment_succeeded":
            subscription_id = data.get("subscription")

            sub = Subscription.objects.filter(
                stripe_subscription_id=subscription_id
            ).first()

            if not sub:
                return Response({"status": "not-found"}, status=200)

            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            period_end = stripe_sub.current_period_end

            sub.expired_at = datetime.fromtimestamp(period_end, tz=timezone.utc)
            sub.save()

            return Response({"status": "renewed"}, status=200)

        # ===================================
        # CANCEL SUBSCRIPTION
        # ===================================
        if event_type == "customer.subscription.deleted":
            subscription_id = data.get("id")

            sub = Subscription.objects.filter(
                stripe_subscription_id=subscription_id
            ).first()

            if not sub:
                return Response({"status": "no-local"}, status=200)

            free_pkg = Package.objects.get(package_name="free")

            sub.current_plan = "free"
            sub.package = free_pkg
            sub.stripe_subscription_id = None
            sub.expired_at = timezone.now() + timedelta(days=7)
            sub.is_active = True
            sub.save()

            return Response({"status": "cancelled → free"}, status=200)

        return Response({"status": "ok"}, status=200)
