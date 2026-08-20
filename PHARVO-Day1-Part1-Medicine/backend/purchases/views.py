from django.db import transaction
from django.db.models import Sum

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from purchases.models import Purchase, PurchaseItem
from purchases.serializers import (
    PurchaseSerializer,
    PurchaseCreateSerializer,
    PurchaseItemSerializer,
)

from inventory.models import (
    Inventory,
    InventoryTransaction,
)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = (
        Purchase.objects
        .select_related(
            "supplier",
            "user",
        )
        .prefetch_related(
            "items",
        )
        .all()
        .order_by("-created_at")
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_serializer_class(self):
        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return PurchaseCreateSerializer

        return PurchaseSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        purchase = serializer.save(
            user=self.request.user
        )

        for item in purchase.items.all():
            inventory, created = (
                Inventory.objects.get_or_create(
                    medicine=item.medicine,
                    defaults={
                        "current_stock": 0,
                        "minimum_stock":
                            item.medicine.minimum_stock,
                    },
                )
            )

            previous_stock = (
                inventory.current_stock
            )

            new_stock = (
                previous_stock
                + item.quantity
            )

            inventory.current_stock = (
                new_stock
            )

            inventory.save()

            InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type="IN",
                quantity=item.quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                note=(
                    f"Purchase #"
                    f"{purchase.invoice_number}"
                ),
            )

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save(
            user=self.request.user
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="total",
    )
    def total_purchase_amount(self, request):
        total = Purchase.objects.aggregate(
            total=Sum("payable_amount")
        )["total"] or 0

        return Response(
            {
                "total_purchase_amount": total
            }
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="supplier-totals",
    )
    def supplier_totals(self, request):
        data = (
            Purchase.objects
            .values(
                "supplier_id",
                "supplier__name",
            )
            .annotate(
                total_purchased=Sum(
                    "payable_amount"
                )
            )
            .order_by(
                "-total_purchased"
            )
        )

        return Response(
            list(data)
        )


class PurchaseItemViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        PurchaseItem.objects
        .select_related(
            "purchase",
            "medicine",
        )
        .all()
    )

    serializer_class = (
        PurchaseItemSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        purchase_id = (
            self.request.query_params.get(
                "purchase"
            )
        )

        if purchase_id:
            queryset = queryset.filter(
                purchase_id=purchase_id
            )

        return queryset