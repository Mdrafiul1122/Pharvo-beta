from django.conf import settings
from django.db import models

from inventory.models import Medicine, Supplier


class Purchase(models.Model):
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="purchases",
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    payable_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    purchase_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Purchase #{self.invoice_number}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name="purchase_items",
        null=True,
        blank=True,
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    manufactured_date = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"