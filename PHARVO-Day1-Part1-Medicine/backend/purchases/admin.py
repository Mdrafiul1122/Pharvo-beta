from django.contrib import admin

from purchases.models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ("medicine", "quantity", "unit_price", "subtotal", "expiry_date")

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "supplier",
        "user",
        "total_amount",
        "discount",
        "payable_amount",
        "purchase_date",
        "created_at",
    )

@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        "purchase",
        "medicine",
        "quantity",
        "unit_price",
        "subtotal",
        "expiry_date",
        "manufactured_date",
    )

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1