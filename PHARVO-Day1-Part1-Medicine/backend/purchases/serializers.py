from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from purchases.models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "purchase",
            "medicine",
            "medicine_name",
            "quantity",
            "unit_price",
            "subtotal",
            "expiry_date",
            "manufactured_date",
        ]
        read_only_fields = [
            "id",
            "purchase",
            "medicine_name",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than 0."
            )
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Unit price cannot be negative."
            )
        return value

    def validate_subtotal(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Subtotal cannot be negative."
            )
        return value

    def validate(self, attrs):
        quantity = attrs.get("quantity")
        unit_price = attrs.get("unit_price")
        subtotal = attrs.get("subtotal")

        if (
            quantity is not None
            and unit_price is not None
            and subtotal is not None
        ):
            expected_subtotal = quantity * unit_price

            if subtotal != expected_subtotal:
                raise serializers.ValidationError(
                    {
                        "subtotal": (
                            f"Subtotal should be {expected_subtotal} "
                            f"(quantity × unit price)."
                        )
                    }
                )

        return attrs


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    user_name = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Purchase
        fields = [
            "id",
            "invoice_number",
            "supplier",
            "supplier_name",
            "user",
            "user_name",
            "total_amount",
            "discount",
            "payable_amount",
            "purchase_date",
            "created_at",
            "items",
        ]


class PurchaseCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "invoice_number",
            "supplier",
            "user",
            "total_amount",
            "discount",
            "payable_amount",
            "purchase_date",
            "items",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]

    def validate_invoice_number(self, value):
        if Purchase.objects.filter(invoice_number=value).exists():
            raise serializers.ValidationError(
                "Invoice number already exists."
            )

        return value

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Discount cannot be negative."
            )

        return value

    def validate(self, attrs):
        total_amount = attrs.get("total_amount")
        discount = attrs.get("discount", Decimal("0.00"))
        payable_amount = attrs.get("payable_amount")

        if total_amount is not None and total_amount < 0:
            raise serializers.ValidationError(
                {"total_amount": "Total amount cannot be negative."}
            )

        if payable_amount is not None and payable_amount < 0:
            raise serializers.ValidationError(
                {"payable_amount": "Payable amount cannot be negative."}
            )

        if (
            total_amount is not None
            and discount is not None
            and payable_amount is not None
        ):
            expected_payable = total_amount - discount

            if expected_payable != payable_amount:
                raise serializers.ValidationError(
                    {
                        "payable_amount": (
                            f"Payable amount should be "
                            f"{expected_payable} "
                            f"(total amount - discount)."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")

        purchase = Purchase.objects.create(
            **validated_data
        )

        for item_data in items_data:
            PurchaseItem.objects.create(
                purchase=purchase,
                **item_data
            )

        return purchase

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if items_data is not None:
            instance.items.all().delete()

            for item_data in items_data:
                PurchaseItem.objects.create(
                    purchase=instance,
                    **item_data
                )

        return instance