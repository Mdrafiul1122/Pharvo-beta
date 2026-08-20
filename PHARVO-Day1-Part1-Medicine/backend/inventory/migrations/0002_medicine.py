from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Medicine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("generic_name", models.CharField(max_length=255)),
                ("manufacturer", models.CharField(max_length=255)),
                ("strength", models.CharField(max_length=100)),
                (
                    "dosage_form",
                    models.CharField(
                        choices=[
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
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "pc_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "strip_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "box_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("minimum_stock", models.PositiveIntegerField(default=0)),
                ("expiry_date", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="medicines",
                        to="inventory.category",
                    ),
                ),
            ],
            options={
                "ordering": ["name", "generic_name"],
                "indexes": [
                    models.Index(fields=["name"], name="inventory_medicine_name_idx"),
                    models.Index(fields=["generic_name"], name="inventory_medicine_generic_idx"),
                    models.Index(fields=["manufacturer"], name="inventory_medicine_manuf_idx"),
                    models.Index(fields=["expiry_date"], name="inventory_medicine_expiry_idx"),
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(strip_price__gte=models.F("pc_price")),
                        name="medicine_strip_price_gte_pc_price",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(box_price__gte=models.F("strip_price")),
                        name="medicine_box_price_gte_strip_price",
                    ),
                ],
            },
        ),
    ]
