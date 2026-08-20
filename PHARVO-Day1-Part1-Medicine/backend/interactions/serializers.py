from django.db.models import Q
from rest_framework import serializers

from interactions.models import DrugInteraction


class DrugInteractionSerializer(
    serializers.ModelSerializer
):
    medicine_a_name = serializers.CharField(
        source="medicine_a.name",
        read_only=True,
    )

    medicine_b_name = serializers.CharField(
        source="medicine_b.name",
        read_only=True,
    )

    class Meta:
        model = DrugInteraction

        fields = [
            "id",
            "medicine_a",
            "medicine_a_name",
            "medicine_b",
            "medicine_b_name",
            "severity",
            "description",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "medicine_a_name",
            "medicine_b_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        medicine_a = attrs.get(
            "medicine_a",
            getattr(
                self.instance,
                "medicine_a",
                None,
            ),
        )

        medicine_b = attrs.get(
            "medicine_b",
            getattr(
                self.instance,
                "medicine_b",
                None,
            ),
        )

        if medicine_a == medicine_b:
            raise serializers.ValidationError(
                {
                    "medicine_b":
                    "A medicine cannot interact with itself."
                }
            )

        duplicate_query = DrugInteraction.objects.filter(
            Q(
                medicine_a=medicine_a,
                medicine_b=medicine_b,
            )
            |
            Q(
                medicine_a=medicine_b,
                medicine_b=medicine_a,
            )
        )

        if self.instance:
            duplicate_query = duplicate_query.exclude(
                pk=self.instance.pk
            )

        if duplicate_query.exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        (
                            "This medicine interaction "
                            "already exists."
                        )
                    ]
                }
            )

        return attrs