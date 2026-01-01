from rest_framework import serializers
from .models import SubscriptionInvoice,Subscription
class CreateSubscriptionSerializer(serializers.Serializer):
    # FRONTEND MUST SEND THIS
    package_id = serializers.IntegerField()

    # Only allow valid billing choices
    plan = serializers.ChoiceField(choices=["free","weekly","monthly", "yearly"])

class SubscriptionInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionInvoice
        fields = [
            "id",
            "plan",
            "transaction_id",
            "stripe_invoice_id",
            "amount",
            "start_date",
            "end_date",
            "payment_date",
            "created_at",
        ]

        

class SubscriptionSerializer(serializers.ModelSerializer):
    invoices = SubscriptionInvoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "package",
            "current_plan",
            "expired_at",
            "is_active",
            "stripe_customer_id",
            "stripe_subscription_id",
            "created_at",
            "invoices",  
        ]
