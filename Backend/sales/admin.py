from django.contrib import admin

from .models import Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "payable_amount", "payment_method", "sale_date")
    list_filter = ("payment_method", "sale_date")
    search_fields = ("invoice_number",)
    inlines = [SaleItemInline, SalePaymentInline]


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = ("sale", "method", "amount", "created_at")
    list_filter = ("method",)
