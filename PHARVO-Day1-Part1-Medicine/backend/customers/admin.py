from django.contrib import admin

from customers.models import (
    Customer,
    CustomerMedicine,
    MedicineReminder,
    MedicineRefillReminder,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone",
        "membership",
        "blood_pressure_systolic",
        "blood_pressure_diastolic",
        "has_diabetes",
        "loyalty_points",
        "created_at",
    ]

    search_fields = [
        "name",
        "phone",
        "email",
    ]

    list_filter = [
        "membership",
        "has_diabetes",
    ]


@admin.register(CustomerMedicine)
class CustomerMedicineAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "medicine",
        "dose",
        "schedule",
        "is_sensitive",
        "permission_status",
    ]

    search_fields = [
        "customer__name",
        "medicine__name",
    ]

    list_filter = [
        "is_sensitive",
        "permission_status",
    ]


@admin.register(MedicineReminder)
class MedicineReminderAdmin(admin.ModelAdmin):
    list_display = [
        "customer_medicine",
        "reminder_time",
        "days_of_week",
        "is_active",
    ]

    list_filter = [
        "is_active",
    ]


@admin.register(MedicineRefillReminder)
class MedicineRefillReminderAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "medicine",
        "refill_date",
        "refill_time",
        "is_active",
        "created_at",
    ]

    search_fields = [
        "customer__name",
        "customer__phone",
        "medicine__name",
    ]

    list_filter = [
        "is_active",
        "refill_date",
    ]

    ordering = [
        "refill_date",
        "refill_time",
    ]