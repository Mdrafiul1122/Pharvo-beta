from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "supplier"
        verbose_name_plural = "suppliers"

    def __str__(self):
        return self.name


class MedicineGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "medicine group"
        verbose_name_plural = "medicine groups"

    def __str__(self):
        return self.name


class DrugInteraction(models.Model):
    class Level(models.TextChoices):
        BENEFICIAL = "beneficial", "Beneficial"
        CAUTION = "caution", "Caution"
        AVOID = "avoid", "Avoid"
        HIGH_RISK = "high_risk", "High Risk"
        CONTRAINDICATED = "contraindicated", "Contraindicated"

    drug_a = models.CharField(max_length=255)
    drug_b = models.CharField(max_length=255)
    interaction_level = models.CharField(
        max_length=20,
        choices=Level.choices,
    )
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    pair_key = models.CharField(
        max_length=511,
        unique=True,
        editable=False,
        help_text="Normalized unordered pair used to prevent duplicate/reversed interactions.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["drug_a", "drug_b"]
        verbose_name = "drug interaction"
        verbose_name_plural = "drug interactions"

    def __str__(self):
        return f"{self.drug_a} + {self.drug_b} ({self.get_interaction_level_display()})"

    @staticmethod
    def build_pair_key(drug_a, drug_b):
        return "||".join(
            sorted((drug_a.strip().lower(), drug_b.strip().lower()))
        )

    def save(self, *args, **kwargs):
        self.pair_key = self.build_pair_key(self.drug_a, self.drug_b)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, default="")
    barcode = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    group = models.ForeignKey(
        MedicineGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="medicine group",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_sensitive = models.BooleanField(
        default=False,
        verbose_name="sensitive medicine",
        help_text="Flag medicines that require staff approval at POS checkout.",
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name
