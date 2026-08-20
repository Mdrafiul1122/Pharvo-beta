from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(
        max_length=255,
        blank=True,
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class MedicineGroup(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.name


class Medicine(models.Model):
    """PHARVO medicine/product master record."""

    DOSAGE_FORM_CHOICES = [
        ("TABLET", "Tablet"),
        ("CAPSULE", "Capsule"),
        ("SYRUP", "Syrup"),
        ("SUSPENSION", "Suspension"),
        ("INJECTION", "Injection"),
        ("CREAM", "Cream"),
        ("OINTMENT", "Ointment"),
        ("DROPS", "Drops"),
        ("INHALER", "Inhaler"),
        ("OTHER", "Other"),
    ]

    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="medicines",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="medicines",
        null=True,
        blank=True,
    )

    medicine_group = models.ForeignKey(
        MedicineGroup,
        on_delete=models.PROTECT,
        related_name="medicines",
        null=True,
        blank=True,
    )

    strength = models.CharField(max_length=100)

    dosage_form = models.CharField(
        max_length=20,
        choices=DOSAGE_FORM_CHOICES,
    )

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    pc_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    strip_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    box_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    pcs_per_strip = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    strips_per_box = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    minimum_stock = models.PositiveIntegerField(
        default=0,
    )

    expiry_date = models.DateField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "name",
            "generic_name",
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    strip_price__gte=models.F("pc_price")
                ),
                name="medicine_strip_price_gte_pc_price",
            ),

            models.CheckConstraint(
                condition=models.Q(
                    box_price__gte=models.F("strip_price")
                ),
                name="medicine_box_price_gte_strip_price",
            ),
        ]

        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["generic_name"]),
            models.Index(fields=["manufacturer"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return (
            f"{self.name} {self.strength} "
            f"({self.dosage_form})"
        )


class Inventory(models.Model):
    medicine = models.OneToOneField(
        Medicine,
        on_delete=models.CASCADE,
        related_name="inventory",
    )

    current_stock = models.PositiveIntegerField(
        default=0,
    )

    minimum_stock = models.PositiveIntegerField(
        default=0,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "medicine__name",
        ]

        indexes = [
            models.Index(fields=["current_stock"]),
            models.Index(fields=["minimum_stock"]),
        ]

    def __str__(self):
        return (
            f"{self.medicine.name} - "
            f"Stock: {self.current_stock}"
        )

    @property
    def is_low_stock(self):
        return (
            self.current_stock
            <= self.minimum_stock
        )

    @property
    def is_expired(self):
        from django.utils import timezone

        return (
            self.medicine.expiry_date
            < timezone.now().date()
        )

    @property
    def is_expiring_soon(self):
        from datetime import timedelta
        from django.utils import timezone

        today = timezone.now().date()

        return (
            today
            <= self.medicine.expiry_date
            <= today + timedelta(days=30)
        )


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("IN", "Stock In"),
        ("OUT", "Stock Out"),
    ]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=3,
        choices=TRANSACTION_TYPES,
    )

    quantity = models.PositiveIntegerField()

    previous_stock = models.PositiveIntegerField()

    new_stock = models.PositiveIntegerField()

    note = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.inventory.medicine.name} - "
            f"{self.transaction_type} - "
            f"{self.quantity}"
        )
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("low_stock", "Low Stock"),
        ("out_of_stock", "Out of Stock"),
        ("expired", "Expired"),
        ("near_expiry", "Near Expiry"),
    ]

    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=["notification_type"]
            ),
            models.Index(
                fields=["severity"]
            ),
            models.Index(
                fields=["is_read"]
            ),
        ]

    def __str__(self):
        return self.title