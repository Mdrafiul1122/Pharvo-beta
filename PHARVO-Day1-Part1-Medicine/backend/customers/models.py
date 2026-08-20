from django.db import models

from inventory.models import Medicine


class Customer(models.Model):
    MEMBERSHIP_CHOICES = [
        ("BRONZE", "Bronze"),
        ("SILVER", "Silver"),
        ("GOLD", "Gold"),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    membership = models.CharField(
        max_length=10,
        choices=MEMBERSHIP_CHOICES,
        default="BRONZE",
    )

    blood_pressure_systolic = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    blood_pressure_diastolic = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    has_diabetes = models.BooleanField(default=False)

    loyalty_points = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class CustomerMedicine(models.Model):
    PERMISSION_STATUS_CHOICES = [
        ("NOT_REQUIRED", "Not Required"),
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="medicines",
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name="customer_medicines",
    )

    dose = models.CharField(
        max_length=100,
    )

    schedule = models.CharField(
        max_length=255,
    )

    is_sensitive = models.BooleanField(
        default=False,
    )

    permission_status = models.CharField(
        max_length=20,
        choices=PERMISSION_STATUS_CHOICES,
        default="NOT_REQUIRED",
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "customer__name",
            "medicine__name",
        ]

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.medicine.name}"
        )


class MedicineReminder(models.Model):
    customer_medicine = models.ForeignKey(
        CustomerMedicine,
        on_delete=models.CASCADE,
        related_name="reminders",
    )

    reminder_time = models.TimeField()

    days_of_week = models.CharField(
        max_length=100,
        default="DAILY",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "reminder_time",
        ]

    def __str__(self):
        return (
            f"{self.customer_medicine.customer.name} - "
            f"{self.customer_medicine.medicine.name} - "
            f"{self.reminder_time}"
        )
        
class MedicineRefillReminder(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="refill_reminders",
    )

    medicine = models.ForeignKey(
        "inventory.Medicine",
        on_delete=models.PROTECT,
        related_name="refill_reminders",
    )

    refill_date = models.DateField(
        db_index=True,
    )

    refill_time = models.TimeField()

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    note = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "refill_date",
            "refill_time",
        ]

    def __str__(self):
        return (
            f"{self.customer.name} - "
            f"{self.medicine.name} - "
            f"{self.refill_date}"
        )