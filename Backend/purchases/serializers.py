from decimal import Decimal

from rest_framework import serializers

from .models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "subtotal",
            "expiry_date",
            "manufactured_date",
        ]
        read_only_fields = ["subtotal"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value

    def validate(self, attrs):
        manufactured_date = attrs.get("manufactured_date")
        expiry_date = attrs.get("expiry_date")
        if manufactured_date and expiry_date and expiry_date < manufactured_date:
            raise serializers.ValidationError(
                "Expiry date cannot be before the manufactured date."
            )
        return attrs

    def create(self, validated_data):
        validated_data["subtotal"] = (
            validated_data["quantity"] * validated_data["unit_price"]
        )
        return super().create(validated_data)


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, required=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "invoice_number",
            "supplier",
            "supplier_name",
            "user",
            "user_username",
            "total_amount",
            "discount",
            "payable_amount",
            "purchase_date",
            "created_at",
            "items",
        ]
        read_only_fields = ["user", "total_amount", "payable_amount", "created_at"]

    @staticmethod
    def _calc_total(items):
        return sum(item["quantity"] * item["unit_price"] for item in items)

    def validate_invoice_number(self, value):
        invoice_number = value.strip()
        if not invoice_number:
            raise serializers.ValidationError("Invoice number cannot be blank.")
        return invoice_number

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value

    def validate(self, attrs):
        items = attrs.get("items")
        discount = attrs.get("discount")
        if self.instance is None:
            if not items:
                raise serializers.ValidationError(
                    {"items": "At least one purchase item is required."}
                )
            total = self._calc_total(items)
        else:
            total = self._calc_total(items) if items else self.instance.total_amount
        if discount is not None and discount > total:
            raise serializers.ValidationError(
                {"discount": "Discount cannot exceed the total amount."}
            )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        validated_data["user"] = self.context["request"].user
        total = self._calc_total(items_data)
        discount = validated_data.get("discount") or Decimal("0")
        validated_data["total_amount"] = total
        validated_data["payable_amount"] = total - discount
        purchase = Purchase.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseItem.objects.create(
                purchase=purchase,
                subtotal=item_data["quantity"] * item_data["unit_price"],
                **item_data,
            )
        return purchase

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        discount = validated_data.get("discount")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if items_data is not None:
            total = self._calc_total(items_data)
            if discount is None:
                discount = instance.discount
            instance.total_amount = total
            instance.payable_amount = total - discount
            instance.save()
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseItem.objects.create(
                    purchase=instance,
                    subtotal=item_data["quantity"] * item_data["unit_price"],
                    **item_data,
                )
        else:
            if discount is not None:
                instance.payable_amount = instance.total_amount - discount
            instance.save()
        return instance
