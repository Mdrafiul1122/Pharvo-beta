from django.db import models


class Medicine(models.Model):
    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True)

    strength = models.CharField(max_length=100, blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)

    pc_price = models.DecimalField(max_digits=10, decimal_places=2)
    strip_price = models.DecimalField(max_digits=10, decimal_places=2)
    box_price = models.DecimalField(max_digits=10, decimal_places=2)

    minimum_stock = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()

    is_sensitive = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["medicine_name"]

    def __str__(self):
        return f"{self.medicine_name} - {self.strength}"