from django.db import transaction
from rest_framework import serializers

from inventory.models import (
    Category,
    Supplier,
    MedicineGroup,
    Medicine,
    Inventory,
    InventoryTransaction,
    Notification,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class MedicineGroupSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = MedicineGroup
        fields = "__all__"


class MedicineSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
        allow_null=True,
    )

    medicine_group_name = serializers.CharField(
        source="medicine_group.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Medicine

        fields = [
            "id",
            "name",
            "generic_name",
            "manufacturer",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "medicine_group",
            "medicine_group_name",
            "strength",
            "dosage_form",
            "cost_price",
            "pc_price",
            "strip_price",
            "box_price",
            "pcs_per_strip",
            "strips_per_box",
            "minimum_stock",
            "expiry_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        pc = attrs.get(
            "pc_price",
            getattr(
                self.instance,
                "pc_price",
                None,
            ),
        )

        strip = attrs.get(
            "strip_price",
            getattr(
                self.instance,
                "strip_price",
                None,
            ),
        )

        box = attrs.get(
            "box_price",
            getattr(
                self.instance,
                "box_price",
                None,
            ),
        )

        if (
            pc is not None
            and strip is not None
            and strip < pc
        ):
            raise serializers.ValidationError(
                {
                    "strip_price":
                    "Strip price cannot be lower than PC price."
                }
            )

        if (
            strip is not None
            and box is not None
            and box < strip
        ):
            raise serializers.ValidationError(
                {
                    "box_price":
                    "Box price cannot be lower than Strip price."
                }
            )

        return attrs


class InventorySerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="medicine.supplier.name",
        read_only=True,
        allow_null=True,
    )

    category_name = serializers.CharField(
        source="medicine.category.name",
        read_only=True,
    )

    expiry_date = serializers.DateField(
        source="medicine.expiry_date",
        read_only=True,
    )

    is_low_stock = serializers.BooleanField(
        read_only=True,
    )

    is_expired = serializers.BooleanField(
        read_only=True,
    )

    is_expiring_soon = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Inventory

        fields = [
            "id",
            "medicine",
            "medicine_name",
            "supplier_name",
            "category_name",
            "current_stock",
            "minimum_stock",
            "expiry_date",
            "is_low_stock",
            "is_expired",
            "is_expiring_soon",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "medicine_name",
            "supplier_name",
            "category_name",
            "expiry_date",
            "is_low_stock",
            "is_expired",
            "is_expiring_soon",
            "updated_at",
        ]


class InventoryTransactionSerializer(
    serializers.ModelSerializer
):
    medicine_name = serializers.CharField(
        source="inventory.medicine.name",
        read_only=True,
    )

    class Meta:
        model = InventoryTransaction

        fields = [
            "id",
            "inventory",
            "medicine_name",
            "transaction_type",
            "quantity",
            "previous_stock",
            "new_stock",
            "note",
            "created_at",
        ]

        read_only_fields = [
            "previous_stock",
            "new_stock",
            "created_at",
        ]

    @transaction.atomic
    def create(self, validated_data):
        inventory_obj = validated_data["inventory"]

        inventory = (
            Inventory.objects
            .select_for_update()
            .get(pk=inventory_obj.pk)
        )

        quantity = validated_data["quantity"]

        transaction_type = validated_data[
            "transaction_type"
        ]

        previous_stock = inventory.current_stock

        if transaction_type == "IN":
            new_stock = (
                previous_stock + quantity
            )

        else:
            if quantity > previous_stock:
                raise serializers.ValidationError(
                    {
                        "quantity":
                        "Insufficient stock."
                    }
                )

            new_stock = (
                previous_stock - quantity
            )

        inventory.current_stock = new_stock
        inventory.save()

        return InventoryTransaction.objects.create(
            inventory=inventory,
            transaction_type=transaction_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            note=validated_data.get(
                "note",
                "",
            ),
        )
class NotificationSerializer(
    serializers.ModelSerializer
):
    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    class Meta:
        model = Notification

        fields = [
            "id",
            "medicine",
            "medicine_name",
            "notification_type",
            "severity",
            "title",
            "message",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "medicine_name",
            "created_at",
        ]