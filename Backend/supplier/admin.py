from django.contrib import admin

from supplier.models import SupplierOrder


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'medicine', 'quantity', 'status', 'requested_date')
    list_filter = ('status',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    search_fields = ('notes',)
