from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from customers.serializers import CustomerSerializer
from sales.models import SalePayment
from sales.serializers import SaleSerializer

from .models import Reminder


class CustomerProfileSerializer(CustomerSerializer):
    total_purchases = serializers.SerializerMethodField()
    total_spending = serializers.SerializerMethodField()

    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + [
            "total_purchases",
            "total_spending",
        ]

    def get_total_purchases(self, obj):
        return obj.sales.count()

    def get_total_spending(self, obj):
        return obj.sales.aggregate(total=Sum("payable_amount"))["total"] or Decimal("0")


class PurchasePaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = SalePayment
        fields = ["method", "method_display", "amount"]


class PurchaseHistorySerializer(SaleSerializer):
    payments = PurchasePaymentSerializer(many=True, read_only=True)

    class Meta(SaleSerializer.Meta):
        fields = SaleSerializer.Meta.fields + ["payments"]


class FrequentProductSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    product_name = serializers.CharField()
    total_quantity = serializers.IntegerField()
    total_spent = serializers.CharField()


class CustomerSummarySerializer(serializers.Serializer):
    customer = CustomerProfileSerializer(read_only=True)
    total_purchases = serializers.IntegerField()
    total_spending = serializers.CharField()
    recent_purchases = PurchaseHistorySerializer(many=True, read_only=True)
    frequently_purchased_products = FrequentProductSerializer(many=True)


class ReminderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Reminder
        fields = [
            "id",
            "customer",
            "customer_name",
            "product",
            "product_name",
            "title",
            "reminder_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_title(self, value):
        title = value.strip()
        if not title:
            raise serializers.ValidationError("Reminder title cannot be blank.")
        return title