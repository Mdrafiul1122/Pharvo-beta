from django.db import models

from inventory.models import Medicine


class DrugInteraction(models.Model):
    SEVERITY_CHOICES = [
        ("MILD", "Mild"),
        ("MODERATE", "Moderate"),
        ("SEVERE", "Severe"),
    ]

    medicine_a = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="interactions_as_a",
    )

    medicine_b = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="interactions_as_b",
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["medicine_a__name", "medicine_b__name"]

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    medicine_a=models.F("medicine_b")
                ),
                name="different_medicines_in_interaction",
            ),

            models.UniqueConstraint(
                fields=[
                    "medicine_a",
                    "medicine_b",
                ],
                name="unique_drug_interaction_pair",
            ),
        ]

    def save(self, *args, **kwargs):
        # Always store the smaller medicine ID first.
        # This prevents A+B and B+A from becoming two records.
        if (
            self.medicine_a_id
            and self.medicine_b_id
            and self.medicine_a_id > self.medicine_b_id
        ):
            self.medicine_a_id, self.medicine_b_id = (
                self.medicine_b_id,
                self.medicine_a_id,
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.medicine_a.name} + "
            f"{self.medicine_b.name} "
            f"({self.severity})"
        )