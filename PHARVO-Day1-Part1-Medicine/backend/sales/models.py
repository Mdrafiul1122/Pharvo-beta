from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from customers.models import Customer
from inventory.models import Medicine


class Sale(models.Model):
    PAYMENT_CHOICES = [
        ("CASH", "Cash"),
        ("CARD", "Card"),
        ("BKASH", "bKash"),
        ("NAGAD","Nagad"),
        ("SPLIT", "Split Payment"),
    ]

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales",
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

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
    )

    sale_date = models.DateField(
        auto_now_add=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sale #{self.invoice_number}"


class SaleItem(models.Model):
    UNIT_CHOICES = [
        ("PC", "PC"),
        ("STRIP", "Strip"),
        ("BOX", "Box"),
    ]

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name="sale_items",
    )

    unit_type = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="PC",
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

    def __str__(self):
        return (
            f"{self.medicine.name} "
            f"x {self.quantity} {self.unit_type}"
        )


class SalePayment(models.Model):
    PAYMENT_CHOICES = [
        ("CASH", "Cash"),
        ("CARD", "Card"),
        ("BKASH", "bKash"),
        ("NAGAD","Nagad"),
    ]

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sale",
                    "payment_method",
                ],
                name="unique_payment_method_per_sale",
            ),
        ]

    def __str__(self):
        return (
            f"{self.sale.invoice_number} - "
            f"{self.payment_method} - "
            f"{self.amount}"
        )