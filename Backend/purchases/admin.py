from django.contrib import admin

from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "supplier", "payable_amount", "purchase_date")
    list_filter = ("purchase_date",)
    search_fields = ("invoice_number",)
    inlines = [PurchaseItemInline]