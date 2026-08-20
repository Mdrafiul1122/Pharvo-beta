from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from interactions.models import DrugInteraction
from interactions.serializers import (
    DrugInteractionSerializer,
)


class DrugInteractionViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        DrugInteraction.objects
        .select_related(
            "medicine_a",
            "medicine_b",
        )
        .all()
    )

    serializer_class = (
        DrugInteractionSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]