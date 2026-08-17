from django.db import models


class Reminder(models.Model):
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="reminders",
    )
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.CASCADE,
        related_name="reminders",
    )
    title = models.CharField(max_length=255)
    reminder_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["reminder_time"]
        verbose_name = "medicine reminder"
        verbose_name_plural = "medicine reminders"

    def __str__(self):
        return f"{self.title} for {self.customer}"
