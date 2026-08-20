from rest_framework import serializers

from customers.models import (
    Customer,
    CustomerMedicine,
    MedicineReminder,
    MedicineRefillReminder,
)


class MedicineReminderSerializer(
    serializers.ModelSerializer
):
    customer_name = serializers.CharField(
        source="customer_medicine.customer.name",
        read_only=True,
    )

    medicine_name = serializers.CharField(
        source="customer_medicine.medicine.name",
        read_only=True,
    )

    class Meta:
        model = MedicineReminder

        fields = [
            "id",
            "customer_medicine",
            "customer_name",
            "medicine_name",
            "reminder_time",
            "days_of_week",
            "is_active",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "customer_name",
            "medicine_name",
            "created_at",
        ]


class MedicineRefillReminderSerializer(
    serializers.ModelSerializer
):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    class Meta:
        model = MedicineRefillReminder

        fields = [
            "id",
            "customer",
            "customer_name",
            "medicine",
            "medicine_name",
            "refill_date",
            "refill_time",
            "is_active",
            "note",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer_name",
            "medicine_name",
            "created_at",
            "updated_at",
        ]


class CustomerMedicineSerializer(
    serializers.ModelSerializer
):
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    medicine_name = serializers.CharField(
        source="medicine.name",
        read_only=True,
    )

    reminders = MedicineReminderSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CustomerMedicine

        fields = [
            "id",
            "customer",
            "customer_name",
            "medicine",
            "medicine_name",
            "dose",
            "schedule",
            "is_sensitive",
            "permission_status",
            "notes",
            "reminders",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer_name",
            "medicine_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        is_sensitive = attrs.get(
            "is_sensitive",
            getattr(
                self.instance,
                "is_sensitive",
                False,
            ),
        )

        permission_status = attrs.get(
            "permission_status",
            getattr(
                self.instance,
                "permission_status",
                "NOT_REQUIRED",
            ),
        )

        if (
            is_sensitive
            and permission_status == "NOT_REQUIRED"
        ):
            raise serializers.ValidationError(
                {
                    "permission_status":
                    (
                        "Sensitive medicine must have "
                        "Pending, Approved, or Rejected status."
                    )
                }
            )

        if (
            not is_sensitive
            and permission_status != "NOT_REQUIRED"
        ):
            raise serializers.ValidationError(
                {
                    "permission_status":
                    (
                        "Non-sensitive medicine should use "
                        "NOT_REQUIRED permission status."
                    )
                }
            )

        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    medicines = CustomerMedicineSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Customer

        fields = [
            "id",
            "name",
            "phone",
            "email",
            "address",
            "membership",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "has_diabetes",
            "loyalty_points",
            "medicines",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate(self, attrs):
        systolic = attrs.get(
            "blood_pressure_systolic",
            getattr(
                self.instance,
                "blood_pressure_systolic",
                None,
            ),
        )

        diastolic = attrs.get(
            "blood_pressure_diastolic",
            getattr(
                self.instance,
                "blood_pressure_diastolic",
                None,
            ),
        )

        if (
            systolic is None
            and diastolic is not None
        ):
            raise serializers.ValidationError(
                {
                    "blood_pressure_systolic":
                    "Systolic BP is required."
                }
            )

        if (
            systolic is not None
            and diastolic is None
        ):
            raise serializers.ValidationError(
                {
                    "blood_pressure_diastolic":
                    "Diastolic BP is required."
                }
            )

        return attrs