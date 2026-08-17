from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        LOW_STOCK = "low_stock", "Low stock"
        OUT_OF_STOCK = "out_of_stock", "Out of stock"
        EXPIRED = "expired", "Expired"
        NEAR_EXPIRY = "near_expiry", "Near expiry"

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default="")
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.WARNING,
    )
    is_read = models.BooleanField(default=False)
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    dedup_key = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        help_text="Stable key (type + product + relevant date/status) used to prevent duplicate alerts.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    def __str__(self):
        return f"{self.type}: {self.title}"