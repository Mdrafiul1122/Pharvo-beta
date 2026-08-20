from django.contrib import admin

from inventory.models import (
    Category,
    Supplier,
    MedicineGroup,
    Medicine,
    Inventory,
    InventoryTransaction,
    Notification,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]

    search_fields = [
        "name",
    ]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "contact_person",
        "phone",
        "email",
    ]

    search_fields = [
        "name",
        "contact_person",
    ]


@admin.register(MedicineGroup)
class MedicineGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]

    search_fields = [
        "name",
    ]


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "generic_name",
        "manufacturer",
        "category",
        "supplier",
        "medicine_group",
        "cost_price",
        "pc_price",
        "strip_price",
        "box_price",
        "minimum_stock",
        "expiry_date",
        "is_active",
    ]

    list_filter = [
        "category",
        "supplier",
        "medicine_group",
        "dosage_form",
        "is_active",
        "expiry_date",
    ]

    search_fields = [
        "name",
        "generic_name",
        "manufacturer",
        "strength",
    ]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        "medicine",
        "current_stock",
        "minimum_stock",
        "updated_at",
    ]


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "inventory",
        "transaction_type",
        "quantity",
        "previous_stock",
        "new_stock",
        "created_at",
    ]

    list_filter = [
        "transaction_type",
    ]
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "medicine",
        "notification_type",
        "severity",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "notification_type",
        "severity",
        "is_read",
    ]

    search_fields = [
        "title",
        "message",
        "medicine__name",
    ]