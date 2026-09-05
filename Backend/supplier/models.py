from django.conf import settings
from django.db import models


class SupplierOrder(models.Model):
    STATUS_REQUESTED = 'REQUESTED'
    STATUS_ORDERED = 'ORDERED'
    STATUS_RECEIVED = 'RECEIVED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'REQUESTED'),
        (STATUS_ORDERED, 'ORDERED'),
        (STATUS_RECEIVED, 'RECEIVED'),
        (STATUS_CANCELLED, 'CANCELLED'),
    ]

    id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(
        'inventory.InventorySupplier',
        models.DO_NOTHING,
        db_column='supplier_id',
        related_name='supplier_orders',
    )
    medicine = models.ForeignKey(
        'inventory.InventoryProduct',
        models.DO_NOTHING,
        db_column='medicine_id',
        related_name='supplier_orders',
    )
    quantity = models.IntegerField()
    requested_date = models.DateTimeField()
    supplier_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(max_length=20, default=STATUS_REQUESTED)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        db_column='confirmed_by_id',
        blank=True,
        null=True,
        related_name='confirmed_supplier_orders',
    )
    confirmed_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'supplier_supplierorder'
