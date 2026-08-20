from django.db import transaction
from decimal import Decimal
from django.db.models import (
    Sum,
    Count,
    Case,
    When,
    F,
    IntegerField,
)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inventory.models import (
    Inventory,
    InventoryTransaction,
)

from sales.models import (
    Sale,
    SaleItem,
    SalePayment,
)

from sales.serializers import (
    SaleSerializer,
    SaleCreateSerializer,
    SaleItemSerializer,
    SalePaymentSerializer,
)


class SaleViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Sale.objects
            .select_related(
                "customer",
                "user",
            )
            .prefetch_related(
                "items",
                "payments",
            )
            .all()
            .order_by("-created_at")
        )

        customer = self.request.query_params.get(
            "customer"
        )

        payment_method = (
            self.request.query_params.get(
                "payment_method"
            )
        )

        if customer:
            queryset = queryset.filter(
                customer_id=customer
            )

        if payment_method:
            queryset = queryset.filter(
                payments__payment_method=(
                    payment_method.upper()
                )
            ).distinct()

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return SaleCreateSerializer

        return SaleSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        sale = self.get_object()

        # Restore inventory before deleting sale.
        for item in sale.items.select_related(
            "medicine"
        ).all():

            medicine = item.medicine

            if item.unit_type == "PC":
                restore_quantity = item.quantity

            elif item.unit_type == "STRIP":
                restore_quantity = (
                    item.quantity
                    * medicine.pcs_per_strip
                )

            elif item.unit_type == "BOX":
                restore_quantity = (
                    item.quantity
                    * medicine.pcs_per_strip
                    * medicine.strips_per_box
                )

            else:
                restore_quantity = 0

            inventory = (
                Inventory.objects
                .select_for_update()
                .get(medicine=medicine)
            )

            previous_stock = (
                inventory.current_stock
            )

            new_stock = (
                previous_stock
                + restore_quantity
            )

            inventory.current_stock = (
                new_stock
            )

            inventory.save()

            InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type="IN",
                quantity=restore_quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                note=(
                    f"Sale cancelled "
                    f"{sale.invoice_number}"
                ),
            )

        sale.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="total",
    )
    def total_sales(self, request):
        total = (
            Sale.objects.aggregate(
                total=Sum("payable_amount")
            )["total"]
            or 0
        )

        return Response(
            {
                "total_sales_amount": total
            }
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="top-selling",
    )
    def top_selling(self, request):
        data = (
            SaleItem.objects
            .values(
                "medicine_id",
                "medicine__name",
            )
            .annotate(
                total_quantity=Sum(
                    Case(
                        When(
                            unit_type="PC",
                            then=F("quantity"),
                        ),
                        When(
                            unit_type="STRIP",
                            then=(
                                F("quantity")
                                * F(
                                    "medicine__pcs_per_strip"
                                )
                            ),
                        ),
                        When(
                            unit_type="BOX",
                            then=(
                                F("quantity")
                                * F(
                                    "medicine__pcs_per_strip"
                                )
                                * F(
                                    "medicine__strips_per_box"
                                )
                            ),
                        ),
                        output_field=IntegerField(),
                    )
                )
            )
            .order_by("-total_quantity")
            .first()
        )

        return Response(
            data or {}
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="payment-summary",
    )
    def payment_summary(self, request):
        data = (
            SalePayment.objects
            .values("payment_method")
            .annotate(
                number_of_sales=Count(
                    "sale",
                    distinct=True,
                ),
                total_amount=Sum("amount"),
            )
            .order_by("payment_method")
        )

        return Response(
            list(data)
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="pharmacist-sales",
    )
    def pharmacist_sales(self, request):
        data = (
            Sale.objects
            .filter(
                user__profile__role="pharmacist"
            )
            .values(
                "user_id",
                "user__username",
            )
            .annotate(
                total_sales=Sum(
                    "payable_amount"
                ),
                number_of_sales=Count("id"),
            )
            .order_by("-total_sales")
        )

        return Response(
            list(data)
        )


class SaleItemViewSet(
    viewsets.ReadOnlyModelViewSet
):
    queryset = (
        SaleItem.objects
        .select_related(
            "sale",
            "medicine",
        )
        .all()
    )

    serializer_class = (
        SaleItemSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]


class SalePaymentViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = SalePaymentSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            SalePayment.objects
            .select_related("sale")
            .all()
            .order_by("-id")
        )

        invoice = self.request.query_params.get(
            "invoice"
        )

        payment_method = (
            self.request.query_params.get(
                "payment_method"
            )
        )

        if invoice:
            queryset = queryset.filter(
                sale__invoice_number=invoice
            )

        if payment_method:
            queryset = queryset.filter(
                payment_method=payment_method.upper()
            )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
    )
    def payment_summary(self, request):
        result = {
            "CASH": Decimal("0.00"),
            "CARD": Decimal("0.00"),
            "BKASH": Decimal("0.00"),
            "NAGAD": Decimal("0.00"),
        }

        data = (
            SalePayment.objects
            .values("payment_method")
            .annotate(
                total=Sum("amount")
            )
        )

        for row in data:
            method = row["payment_method"]

            if method in result:
                result[method] = (
                    row["total"]
                    or Decimal("0.00")
                )

        return Response(
            {
                "cash": result["CASH"],
                "card": result["CARD"],
                "bkash": result["BKASH"],
                "nagad": result["NAGAD"],
            }
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="method-totals",
    )
    def method_totals(self, request):
        data = (
            SalePayment.objects
            .values("payment_method")
            .annotate(
                total_received=Sum("amount"),
                payment_count=Count("id"),
            )
            .order_by("payment_method")
        )

        return Response(
            list(data)
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="underpaid-invoices",
    )
    def underpaid_invoices(self, request):
        result = []

        sales = (
            Sale.objects
            .prefetch_related("payments")
            .all()
        )

        for sale in sales:
            total_paid = sum(
                (
                    payment.amount
                    for payment
                    in sale.payments.all()
                ),
                Decimal("0.00"),
            )

            if total_paid < sale.payable_amount:
                result.append(
                    {
                        "sale_id": sale.id,
                        "invoice_number":
                            sale.invoice_number,
                        "payable_amount":
                            sale.payable_amount,
                        "total_paid":
                            total_paid,
                        "due_amount":
                            (
                                sale.payable_amount
                                - total_paid
                            ),
                    }
                )

        return Response(result)

    @action(
        detail=False,
        methods=["get"],
        url_path="split-invoices",
    )
    def split_invoices(self, request):
        sales = (
            Sale.objects
            .annotate(
                payment_method_count=Count(
                    "payments__payment_method",
                    distinct=True,
                )
            )
            .filter(
                payment_method_count__gt=1
            )
            .order_by("-created_at")
        )

        result = []

        for sale in sales:
            result.append(
                {
                    "sale_id": sale.id,
                    "invoice_number":
                        sale.invoice_number,
                    "payable_amount":
                        sale.payable_amount,
                    "payment_method_count":
                        sale.payment_method_count,
                }
            )

        return Response(result)