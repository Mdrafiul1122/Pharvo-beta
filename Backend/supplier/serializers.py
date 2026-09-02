from rest_framework import serializers

from inventory.models import InventoryProduct, InventorySupplier
from sales.serializers import PosUserSerializer, ProductBriefSerializer
from supplier.models import SupplierOrder


class SupplierBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySupplier
        fields = ['id', 'name', 'contact_person', 'phone', 'email']


class SupplierOrderSerializer(serializers.ModelSerializer):
    supplier = SupplierBriefSerializer(read_only=True)
    medicine = ProductBriefSerializer(read_only=True)
    confirmed_by = PosUserSerializer(read_only=True)

    class Meta:
        model = SupplierOrder
        fields = [
            'id',
            'supplier',
            'supplier_id',
            'medicine',
            'medicine_id',
            'quantity',
            'requested_date',
            'supplier_price',
            'status',
            'confirmed_by',
            'confirmed_by_id',
            'confirmed_date',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class SupplierOrderCreateSerializer(serializers.Serializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=InventorySupplier.objects.all())
    medicine = serializers.PrimaryKeyRelatedField(queryset=InventoryProduct.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    supplier_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True, min_value=0
    )
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class SupplierOrderUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=SupplierOrder.STATUS_CHOICES, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    supplier_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True, min_value=0
    )
