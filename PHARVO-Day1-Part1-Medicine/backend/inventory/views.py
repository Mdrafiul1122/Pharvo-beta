from datetime import timedelta

from django.db.models import F
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from inventory.models import (
    Category,
    Supplier,
    MedicineGroup,
    Medicine,
    Inventory,
    InventoryTransaction,
    Notification,
)

from inventory.serializers import (
    CategorySerializer,
    SupplierSerializer,
    MedicineGroupSerializer,
    MedicineSerializer,
    InventorySerializer,
    InventoryTransactionSerializer,
    NotificationSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]


class MedicineGroupViewSet(
    viewsets.ModelViewSet
):
    queryset = MedicineGroup.objects.all()

    serializer_class = (
        MedicineGroupSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]


class MedicineViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Medicine.objects
            .select_related(
                "category",
                "supplier",
                "medicine_group",
            )
            .all()
        )

        supplier = (
            self.request.query_params.get(
                "supplier"
            )
        )

        category = (
            self.request.query_params.get(
                "category"
            )
        )

        medicine_group = (
            self.request.query_params.get(
                "medicine_group"
            )
        )

        if supplier:
            queryset = queryset.filter(
                supplier_id=supplier
            )

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        if medicine_group:
            queryset = queryset.filter(
                medicine_group_id=medicine_group
            )

        return queryset


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Inventory.objects
            .select_related(
                "medicine",
                "medicine__supplier",
                "medicine__category",
            )
            .all()
        )

        low_stock = (
            self.request.query_params.get(
                "low_stock"
            )
        )

        expired = (
            self.request.query_params.get(
                "expired"
            )
        )

        expiring_soon = (
            self.request.query_params.get(
                "expiring_soon"
            )
        )

        if low_stock == "true":
            queryset = queryset.filter(
                current_stock__lte=F(
                    "minimum_stock"
                )
            )

        if expired == "true":
            queryset = queryset.filter(
                medicine__expiry_date__lt=(
                    timezone.now().date()
                )
            )

        if expiring_soon == "true":
            today = timezone.now().date()

            queryset = queryset.filter(
                medicine__expiry_date__gte=today,
                medicine__expiry_date__lte=(
                    today + timedelta(days=30)
                ),
            )

        return queryset


class InventoryTransactionViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        InventoryTransaction.objects
        .select_related(
            "inventory",
            "inventory__medicine",
        )
        .all()
    )

    serializer_class = (
        InventoryTransactionSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]
class NotificationViewSet(
    viewsets.ModelViewSet
):
    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Notification.objects
            .select_related("medicine")
            .all()
        )

        notification_type = (
            self.request.query_params.get(
                "type"
            )
        )

        severity = (
            self.request.query_params.get(
                "severity"
            )
        )

        is_read = (
            self.request.query_params.get(
                "is_read"
            )
        )

        if notification_type:
            queryset = queryset.filter(
                notification_type=notification_type
            )

        if severity:
            queryset = queryset.filter(
                severity=severity
            )

        if is_read == "true":
            queryset = queryset.filter(
                is_read=True
            )

        elif is_read == "false":
            queryset = queryset.filter(
                is_read=False
            )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="low-stock",
    )
    def low_stock(self, request):
        queryset = self.get_queryset().filter(
            notification_type="low_stock"
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="unread",
    )
    def unread(self, request):
        queryset = self.get_queryset().filter(
            is_read=False
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="expired",
    )
    def expired(self, request):
        queryset = self.get_queryset().filter(
            notification_type="expired"
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="near-expiry",
    )
    def near_expiry(self, request):
        queryset = self.get_queryset().filter(
            notification_type="near_expiry"
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="critical",
    )
    def critical(self, request):
        queryset = self.get_queryset().filter(
            severity="critical"
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="warning",
    )
    def warning(self, request):
        queryset = self.get_queryset().filter(
            severity="warning"
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="info",
    )
    def info(self, request):
        queryset = self.get_queryset().filter(
            severity="info"
        )

        return Response(
            self.get_serializer(
                queryset,
                many=True,
            ).data
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="mark-read",
    )
    def mark_read(self, request, pk=None):
        notification = self.get_object()

        notification.is_read = True
        notification.save(
            update_fields=["is_read"]
        )

        return Response(
            {
            "message": "Notification marked as read.",
            "id": notification.id,
            "is_read": notification.is_read,
            }
        )