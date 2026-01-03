# payments/views.py
import stripe
from datetime import datetime, timedelta, timezone as dt_timezone
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from notifications.utils import create_notification
from .models import Subscription, Package, SubscriptionInvoice
from .helpers import schedule_subscription
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan = request.data.get("plan")
        package_id = request.data.get("package_id")

        if plan not in ["free", "weekly", "monthly", "yearly"]:
            return Response({"error": "Invalid plan"}, status=400)

        try:
            pkg = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({"error": "Invalid package"}, status=400)

        # -----------------------
        # Stripe customer
        # -----------------------
        prev_sub = Subscription.objects.filter(
            user=user, stripe_customer_id__isnull=False
        ).first()

        if prev_sub:
            stripe_customer_id = prev_sub.stripe_customer_id
        else:
            customer = stripe.Customer.create(email=user.email)
            stripe_customer_id = customer.id

        # -----------------------
        # FREE PLAN (no Stripe)
        # -----------------------
        if plan == "free":
            start, end, is_active = schedule_subscription(user, "free")

            Subscription.objects.create(
                user=user,
                package=pkg,
                current_plan="free",
                expired_at=end,
                is_active=is_active,
            )

            return Response({
                "status": "free-scheduled",
                "starts": start,
                "ends": end,
            })

        # -----------------------
        # Paid plans
        # -----------------------
        price_id = {
            "weekly": pkg.stripe_weekly_price_id,
            "monthly": pkg.stripe_monthly_price_id,
            "yearly": pkg.stripe_yearly_price_id,
        }.get(plan)

        if not price_id:
            return Response({"error": "Stripe price not set"}, status=400)

        # 🔥 Always create NEW subscription row (inactive)
        sub = Subscription.objects.create(
            user=user,
            package=pkg,
            current_plan=plan,
            stripe_customer_id=stripe_customer_id,
            is_active=False,
        )

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=stripe_customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "subscription_db_id": sub.id,  # 🔑 very important
            },
            success_url="biblejourney://payment-success",
            cancel_url="http://localhost:8000/cancel/",
        )

        return Response({"checkout_url": session.url})


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhook(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = []

    def post(self, request):
        payload = request.body
        sig = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception:
            return Response({"error": "invalid signature"}, status=400)

        data = event["data"]["object"]
        event_type = event["type"]

        # ====================================
        # CHECKOUT COMPLETED
        # ====================================
        if event_type == "checkout.session.completed":
            sub_id = data.get("metadata", {}).get("subscription_db_id")

            if not sub_id:
                return Response({"status": "ignored"}, status=200)

            sub = Subscription.objects.get(id=sub_id)

            start, end, is_active = schedule_subscription(
                sub.user, sub.current_plan
            )

            sub.stripe_subscription_id = data.get("subscription")
            sub.expired_at = end
            sub.is_active = is_active
            sub.save()

            return Response({"status": "subscription-scheduled"}, status=200)

        # ====================================
        # INVOICE PAID
        # ====================================
        if event_type == "invoice.payment_succeeded":
            invoice_id = data.get("id")
            payment_intent = data.get("payment_intent")

            subscription_id = (
                data.get("subscription")
                or data.get("parent", {})
                    .get("subscription_details", {})
                    .get("subscription")
            )
            if not subscription_id:
                
                return Response({"status": "no-subscription-id"}, status=200)
            try:
                sub = Subscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
            except Subscription.DoesNotExist:
               
                return Response({"status": "no-sub"}, status=200)

            if SubscriptionInvoice.objects.filter(
                stripe_invoice_id=invoice_id
            ).exists():
                return Response({"status": "duplicate"}, status=200)

            period = data["lines"]["data"][0]["period"]

            now = timezone.now()

            last_sub = (
                Subscription.objects
                .filter(user=sub.user)
                .exclude(id=sub.id)
                .order_by("-expired_at")
                .first()
            )
            if last_sub and last_sub.expired_at and last_sub.expired_at > now:
                start_date = last_sub.expired_at
            else:
                start_date = datetime.fromtimestamp(
                period["start"], tz=dt_timezone.utc
                )
            PLAN_DAYS = {
                "weekly": 7,
                "monthly": 30,
                "yearly": 365,
            }

            end_date = start_date + timedelta(days=PLAN_DAYS[sub.current_plan])

            SubscriptionInvoice.objects.create(
                subscription=sub,
                user=sub.user,
                package=sub.package,
                plan=sub.current_plan,
                transaction_id=payment_intent or invoice_id,
                stripe_invoice_id=invoice_id,
                amount=data["amount_paid"] / 100,
                start_date=start_date,
                end_date=end_date,
                payment_date=timezone.now(),
            )

            create_notification(
                user=sub.user,
                title="🎉 Payment Successful",
                message=f"Your {sub.current_plan.capitalize()} subscription has been activated successfully.",
                n_type="payment"
            )
            
            return Response({"status": "invoice-saved"}, status=200)


        return Response({"status": "ignored"}, status=200)




from payments.serializers import SubscriptionSerializer




class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = (
            Subscription.objects
            .filter(user=request.user)
            .prefetch_related("invoices")
            .order_by("-created_at")
        )

        if not subscriptions.exists():
            return Response(
                {"detail": "No subscription found"},
                status=404
            )

        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


from django.shortcuts import get_object_or_404


class CurrentPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):

        # ==========================
        # CASE 1: Invoice detail
        # ==========================
        if id is not None:
            invoice = get_object_or_404(
                Subscription,
                id=id,
                user=request.user
            )

            serializer = SubscriptionSerializer(invoice)
            return Response(serializer.data)

        # ==========================
        # CASE 2: Active subscription
        # ==========================
        subscription = (
            Subscription.objects
            .filter(user=request.user, is_active=True)
            .prefetch_related("invoices")
            .order_by("-created_at")
            .first()
        )

        if not subscription:
            return Response(
                {"detail": "No active subscription"},
                status=404
            )

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)



from payments.utils import generate_invoice_pdf


class InvoicePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        invoice = get_object_or_404(
            SubscriptionInvoice,
            id=invoice_id,
            user=request.user   
        )

        return generate_invoice_pdf(invoice)
