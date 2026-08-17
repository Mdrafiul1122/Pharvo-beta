from datetime import date

from rest_framework import serializers

from .models import (
    Category,
    DrugInteraction,
    MedicineGroup,
    Product,
    Supplier,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Category name cannot be blank.")
        return name


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Supplier name cannot be blank.")
        return name


class MedicineGroupSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = MedicineGroup
        fields = ["id", "name", "description", "product_count", "created_at"]
        read_only_fields = ["created_at"]

    def get_product_count(self, obj):
        return getattr(obj, "product_count", obj.products.count())

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Group name cannot be blank.")
        return name


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "barcode",
            "category",
            "category_name",
            "group",
            "group_name",
            "supplier",
            "supplier_name",
            "unit_price",
            "cost_price",
            "stock_quantity",
            "reorder_level",
            "expiry_date",
            "is_active",
            "is_sensitive",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Product name cannot be blank.")
        return name

    def validate_barcode(self, value):
        barcode = value.strip()
        if not barcode:
            raise serializers.ValidationError("Barcode cannot be blank.")
        return barcode

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value

    def validate_cost_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost price cannot be negative.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value

    def validate_reorder_level(self, value):
        if value < 0:
            raise serializers.ValidationError("Reorder level cannot be negative.")
        return value

    def validate_expiry_date(self, value):
        if value is not None and value < date.today():
            raise serializers.ValidationError("Expiry date cannot be in the past.")
        return value


class DrugInteractionSerializer(serializers.ModelSerializer):
    interaction_level = serializers.ChoiceField(choices=DrugInteraction.Level.choices)

    class Meta:
        model = DrugInteraction
        fields = [
            "id",
            "drug_a",
            "drug_b",
            "interaction_level",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_drug_a(self, value):
        drug_a = value.strip()
        if not drug_a:
            raise serializers.ValidationError("Drug A cannot be blank.")
        return drug_a

    def validate_drug_b(self, value):
        drug_b = value.strip()
        if not drug_b:
            raise serializers.ValidationError("Drug B cannot be blank.")
        return drug_b

    def validate(self, attrs):
        drug_a = (attrs.get("drug_a") or self.instance.drug_a).strip().lower()
        drug_b = (attrs.get("drug_b") or self.instance.drug_b).strip().lower()
        if drug_a == drug_b:
            raise serializers.ValidationError(
                {"drug_b": "A drug cannot interact with itself."}
            )
        pair_key = DrugInteraction.build_pair_key(drug_a, drug_b)
        duplicate = DrugInteraction.objects.filter(pair_key=pair_key)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError(
                "This interaction pair already exists (in either order)."
            )
        return attrs
