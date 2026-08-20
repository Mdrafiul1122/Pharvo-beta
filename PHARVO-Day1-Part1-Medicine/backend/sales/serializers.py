from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from rest_framework import serializers

from inventory.models import (
    Inventory,
    InventoryTransaction,
)

from sales.models import (
    Sale,
    SaleItem,
    SalePayment,
)


class SaleItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    class Meta:
        model = SaleItem

        fields = [
            "id",
            "medicine",
            "medicine_name",
            "unit_type",
            "quantity",
            "unit_price",
            "subtotal",
        ]

        read_only_fields = [
            "id",
            "medicine_name",
            "unit_price",
            "subtotal",
        ]


class SalePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePayment

        fields = [
            "id",
            "payment_method",
            "amount",
        ]

        read_only_fields = [
            "id",
        ]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(
        many=True,
        read_only=True,
    )

    payments = SalePaymentSerializer(
        many=True,
        read_only=True,
    )

    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    user_name = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Sale

        fields = [
            "id",
            "invoice_number",
            "customer",
            "customer_name",
            "user",
            "user_name",
            "total_amount",
            "discount",
            "payable_amount",
            "payment_method",
            "sale_date",
            "created_at",
            "items",
            "payments",
        ]


class SaleCreateSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        required=False,
    )

    items = SaleItemSerializer(
        many=True,
    )

    payments = SalePaymentSerializer(
        many=True,
    )

    class Meta:
        model = Sale

        fields = [
            "id",
            "invoice_number",
            "customer",
            "user",
            "total_amount",
            "discount",
            "payable_amount",
            "payment_method",
            "sale_date",
            "created_at",
            "items",
            "payments",
        ]

        read_only_fields = [
            "id",
            "user",
            "total_amount",
            "payable_amount",
            "payment_method",
            "sale_date",
            "created_at",
        ]

    def validate(self, attrs):
        items = attrs.get("items", [])
        payments = attrs.get("payments", [])

        if not items:
            raise serializers.ValidationError(
                {
                    "items":
                    "At least one sale item is required."
                }
            )

        if not payments:
            raise serializers.ValidationError(
                {
                    "payments":
                    "At least one payment is required."
                }
            )

        methods = [
            payment["payment_method"]
            for payment in payments
        ]

        if len(methods) != len(set(methods)):
            raise serializers.ValidationError(
                {
                    "payments":
                    "Duplicate payment method is not allowed."
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        payments_data = validated_data.pop("payments")

        invoice_number = validated_data.pop(
            "invoice_number",
            None,
        )

        if not invoice_number:
            invoice_number = (
                f"INV-{uuid4().hex[:10].upper()}"
            )

        discount = validated_data.get(
            "discount",
            Decimal("0.00"),
        )

        total_amount = Decimal("0.00")

        calculated_items = []

        required_stock = {}

        for item in items_data:
            medicine = item["medicine"]
            quantity = item["quantity"]
            unit_type = item["unit_type"]

            if unit_type == "PC":
                unit_price = medicine.pc_price
                stock_quantity = quantity

            elif unit_type == "STRIP":
                unit_price = medicine.strip_price

                stock_quantity = (
                    quantity
                    * medicine.pcs_per_strip
                )

            elif unit_type == "BOX":
                unit_price = medicine.box_price

                stock_quantity = (
                    quantity
                    * medicine.pcs_per_strip
                    * medicine.strips_per_box
                )

            else:
                raise serializers.ValidationError(
                    {
                        "unit_type":
                        "Invalid sale unit."
                    }
                )

            subtotal = (
                unit_price
                * quantity
            )

            total_amount += subtotal

            calculated_items.append(
                {
                    "medicine": medicine,
                    "quantity": quantity,
                    "unit_type": unit_type,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                }
            )

            if medicine.id not in required_stock:
                required_stock[medicine.id] = {
                    "medicine": medicine,
                    "quantity": 0,
                }

            required_stock[medicine.id][
                "quantity"
            ] += stock_quantity

        payable_amount = (
            total_amount
            - discount
        )

        if payable_amount < 0:
            raise serializers.ValidationError(
                {
                    "discount":
                    "Discount cannot exceed total amount."
                }
            )

        payment_total = sum(
            (
                payment["amount"]
                for payment in payments_data
            ),
            Decimal("0.00"),
        )

        if payment_total != payable_amount:
            raise serializers.ValidationError(
                {
                    "payments":
                    (
                        "Payment total must equal "
                        f"payable amount "
                        f"{payable_amount}."
                    )
                }
            )

        inventory_rows = {}

        for medicine_id, stock_data in (
            required_stock.items()
        ):
            try:
                inventory = (
                    Inventory.objects
                    .select_for_update()
                    .get(
                        medicine_id=medicine_id
                    )
                )

            except Inventory.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "inventory":
                        (
                            "Inventory not found for "
                            f"{stock_data['medicine'].name}."
                        )
                    }
                )

            required_quantity = (
                stock_data["quantity"]
            )

            if (
                inventory.current_stock
                < required_quantity
            ):
                raise serializers.ValidationError(
                    {
                        "stock":
                        (
                            "Insufficient stock for "
                            f"{stock_data['medicine'].name}. "
                            f"Available: "
                            f"{inventory.current_stock} PC, "
                            f"Required: "
                            f"{required_quantity} PC."
                        )
                    }
                )

            inventory_rows[
                medicine_id
            ] = inventory

        if len(payments_data) == 1:
            sale_payment_method = (
                payments_data[0][
                    "payment_method"
                ]
            )

        else:
            sale_payment_method = "SPLIT"

        sale = Sale.objects.create(
            invoice_number=invoice_number,
            total_amount=total_amount,
            payable_amount=payable_amount,
            payment_method=sale_payment_method,
            **validated_data,
        )

        for item in calculated_items:
            SaleItem.objects.create(
                sale=sale,
                **item,
            )

        for payment in payments_data:
            SalePayment.objects.create(
                sale=sale,
                **payment,
            )

        for medicine_id, stock_data in (
            required_stock.items()
        ):
            inventory = inventory_rows[
                medicine_id
            ]

            previous_stock = (
                inventory.current_stock
            )

            quantity_out = (
                stock_data["quantity"]
            )

            new_stock = (
                previous_stock
                - quantity_out
            )

            inventory.current_stock = (
                new_stock
            )

            inventory.save()

            InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type="OUT",
                quantity=quantity_out,
                previous_stock=previous_stock,
                new_stock=new_stock,
                note=(
                    f"POS Sale "
                    f"{invoice_number}"
                ),
            )

        return sale