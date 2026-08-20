from django.contrib import admin

from sales.models import (
    Sale,
    SaleItem,
    SalePayment,
)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "customer",
        "total_amount",
        "discount",
        "payable_amount",
        "payment_method",
        "sale_date",
    ]

    search_fields = [
        "invoice_number",
    ]

    list_filter = [
        "payment_method",
        "sale_date",
    ]

    inlines = [
        SaleItemInline,
        SalePaymentInline,
    ]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = [
        "sale",
        "medicine",
        "unit_type",
        "quantity",
        "unit_price",
        "subtotal",
    ]


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = [
        "sale",
        "payment_method",
        "amount",
    ]