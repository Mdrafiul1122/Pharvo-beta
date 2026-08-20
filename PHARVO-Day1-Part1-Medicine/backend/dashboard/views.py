from decimal import Decimal
from datetime import timedelta

from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sales.models import Sale, SaleItem, SalePayment
from purchases.models import Purchase
from inventory.models import (
    Medicine,
    Inventory,
    Supplier,
    Category,
)
from customers.models import Customer


class OwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        # -------------------------
        # SALES
        # -------------------------
        total_sales = Sale.objects.aggregate(
            total=Coalesce(
                Sum("payable_amount"),
                Decimal("0.00"),
            )
        )["total"]

        total_sales_count = Sale.objects.count()

        # -------------------------
        # PURCHASE COST
        # Simplified project profit:
        # sales revenue - purchase expenses
        # -------------------------
        total_purchase_cost = Purchase.objects.aggregate(
            total=Coalesce(
                Sum("payable_amount"),
                Decimal("0.00"),
            )
        )["total"]

        total_profit = total_sales - total_purchase_cost

        # -------------------------
        # INVENTORY
        # -------------------------
        current_stock = Inventory.objects.aggregate(
            total=Coalesce(
                Sum("current_stock"),
                0,
            )
        )["total"]

        low_stock_qs = (
            Inventory.objects
            .select_related("medicine")
            .filter(
                current_stock__lte=models.F("minimum_stock")
            )
        )

        expired_qs = (
            Inventory.objects
            .select_related("medicine")
            .filter(
                medicine__expiry_date__lt=today
            )
        )

        expiring_soon_date = today + timedelta(days=30)

        expiring_soon_qs = (
            Inventory.objects
            .select_related("medicine")
            .filter(
                medicine__expiry_date__gte=today,
                medicine__expiry_date__lte=expiring_soon_date,
            )
        )

        # -------------------------
        # SALES CHART
        # -------------------------
        sales_chart = list(
            Sale.objects
            .values("sale_date")
            .annotate(
                total_sales=Sum("payable_amount"),
                invoice_count=Count("id"),
            )
            .order_by("sale_date")
        )

        for row in sales_chart:
            row["sale_date"] = str(row["sale_date"])
            row["total_sales"] = str(
                row["total_sales"] or Decimal("0.00")
            )

        # -------------------------
        # INVENTORY CHART
        # -------------------------
        inventory_chart = []

        inventories = (
            Inventory.objects
            .select_related("medicine")
            .order_by("medicine__name")
        )

        for inventory in inventories:
            inventory_chart.append(
                {
                    "medicine_id": inventory.medicine_id,
                    "medicine_name": inventory.medicine.name,
                    "current_stock": inventory.current_stock,
                    "minimum_stock": inventory.minimum_stock,
                }
            )

        # -------------------------
        # LOW STOCK REPORT
        # -------------------------
        low_stock = []

        for inventory in low_stock_qs:
            low_stock.append(
                {
                    "medicine_id": inventory.medicine_id,
                    "medicine_name": inventory.medicine.name,
                    "current_stock": inventory.current_stock,
                    "minimum_stock": inventory.minimum_stock,
                }
            )

        # -------------------------
        # EXPIRED REPORT
        # -------------------------
        expired_medicines = []

        for inventory in expired_qs:
            expired_medicines.append(
                {
                    "medicine_id": inventory.medicine_id,
                    "medicine_name": inventory.medicine.name,
                    "expiry_date": str(
                        inventory.medicine.expiry_date
                    ),
                }
            )

        # -------------------------
        # EXPIRING SOON REPORT
        # -------------------------
        expiring_soon = []

        for inventory in expiring_soon_qs:
            expiring_soon.append(
                {
                    "medicine_id": inventory.medicine_id,
                    "medicine_name": inventory.medicine.name,
                    "expiry_date": str(
                        inventory.medicine.expiry_date
                    ),
                }
            )

        return Response(
            {
                "summary": {
                    "total_sales": str(total_sales),
                    "total_purchase_cost": str(
                        total_purchase_cost
                    ),
                    "total_profit": str(total_profit),
                    "current_stock": current_stock,
                    "total_medicines": Medicine.objects.count(),
                    "total_customers": Customer.objects.count(),
                    "total_sales_count": total_sales_count,
                    "low_stock_count": low_stock_qs.count(),
                    "expired_count": expired_qs.count(),
                    "expiring_soon_count": (
                        expiring_soon_qs.count()
                    ),
                },

                "low_stock_medicines": low_stock,

                "expired_medicines": expired_medicines,

                "expiring_soon_medicines": expiring_soon,

                "sales_chart": sales_chart,

                "inventory_chart": inventory_chart,
            }
        )
class AdvancedReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import (
            Sum,
            Count,
            Avg,
            Max,
            F,
            Case,
            When,
            IntegerField,
            DecimalField,
            ExpressionWrapper,
        )
        from django.db.models.functions import (
            TruncMonth,
            Coalesce,
        )

        # =========================================================
        # 1. TOP 5 BEST-SELLING MEDICINES
        # =========================================================

        top_5_medicines = list(
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
            .order_by("-total_quantity")[:5]
        )

        # =========================================================
        # 2. SUPPLIER WITH HIGHEST NUMBER OF MEDICINES
        # =========================================================

        supplier_highest_medicines = list(
            Supplier.objects
            .annotate(
                medicine_count=Count(
                    "medicines",
                    distinct=True,
                )
            )
            .values(
                "id",
                "name",
                "medicine_count",
            )
            .order_by("-medicine_count")[:1]
        )

        # =========================================================
        # 3. CUSTOMERS WHO SPENT > 10,000 BDT
        # =========================================================

        customers_over_10000 = list(
            Customer.objects
            .annotate(
                total_purchase=Coalesce(
                    Sum("sales__payable_amount"),
                    Decimal("0.00"),
                )
            )
            .filter(
                total_purchase__gt=Decimal("10000")
            )
            .values(
                "id",
                "name",
                "phone",
                "total_purchase",
            )
            .order_by("-total_purchase")
        )

        # =========================================================
        # 4. TOTAL REVENUE
        # =========================================================

        total_revenue = (
            Sale.objects.aggregate(
                total=Coalesce(
                    Sum("payable_amount"),
                    Decimal("0.00"),
                )
            )["total"]
        )

        # =========================================================
        # 5. TOTAL PURCHASE COST
        # =========================================================

        total_purchase_cost = (
            Purchase.objects.aggregate(
                total=Coalesce(
                    Sum("payable_amount"),
                    Decimal("0.00"),
                )
            )["total"]
        )

        # =========================================================
        # 6. SALES - PURCHASE COST
        # =========================================================

        profit_difference = (
            total_revenue
            - total_purchase_cost
        )

        # =========================================================
        # 7. LOW STOCK + NEAR EXPIRY
        # =========================================================

        low_stock_near_expiry = list(
            Inventory.objects
            .select_related("medicine")
            .filter(
                current_stock__lte=F(
                    "minimum_stock"
                ),
                medicine__expiry_date__gte=
                    timezone.now().date(),
                medicine__expiry_date__lte=(
                    timezone.now().date()
                    + timedelta(days=30)
                ),
            )
            .values(
                "medicine_id",
                "medicine__name",
                "current_stock",
                "minimum_stock",
                "medicine__expiry_date",
            )
        )

        # =========================================================
        # 8. CUSTOMER WHO SPENT THE MOST
        # =========================================================

        highest_spending_customer = list(
            Customer.objects
            .annotate(
                total_spent=Coalesce(
                    Sum("sales__payable_amount"),
                    Decimal("0.00"),
                )
            )
            .values(
                "id",
                "name",
                "total_spent",
            )
            .order_by("-total_spent")[:1]
        )

        # =========================================================
        # 9. PAYMENT METHOD WITH HIGHEST SALES
        # =========================================================

        highest_payment_method = list(
            SalePayment.objects
            .values("payment_method")
            .annotate(
                total_amount=Sum("amount")
            )
            .order_by("-total_amount")[:1]
        )

        # =========================================================
        # 10. MONTHLY SALES TOTAL
        # =========================================================

        monthly_sales = list(
            Sale.objects
            .annotate(
                month=TruncMonth("sale_date")
            )
            .values("month")
            .annotate(
                total_sales=Sum(
                    "payable_amount"
                ),
                number_of_sales=Count("id"),
            )
            .order_by("month")
        )

        # =========================================================
        # 11. MONTHLY PURCHASE TOTAL
        # =========================================================

        monthly_purchases = list(
            Purchase.objects
            .annotate(
                month=TruncMonth(
                    "purchase_date"
                )
            )
            .values("month")
            .annotate(
                total_purchase=Sum(
                    "payable_amount"
                ),
                number_of_purchases=Count("id"),
            )
            .order_by("month")
        )

        # =========================================================
        # 12. MEDICINES SOLD BY EACH PHARMACIST
        # =========================================================

        medicines_by_pharmacist = list(
            SaleItem.objects
            .filter(
                sale__user__profile__role=
                    "pharmacist"
            )
            .values(
                "sale__user_id",
                "sale__user__username",
            )
            .annotate(
                total_medicines_sold=Sum(
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
            .order_by(
                "-total_medicines_sold"
            )
        )

        # =========================================================
        # 13. NUMBER OF SALES BY EACH PHARMACIST
        # =========================================================

        sales_by_pharmacist = list(
            Sale.objects
            .filter(
                user__profile__role="pharmacist"
            )
            .values(
                "user_id",
                "user__username",
            )
            .annotate(
                number_of_sales=Count("id")
            )
            .order_by(
                "-number_of_sales"
            )
        )

        # =========================================================
        # 14. CUSTOMERS WITH NO PURCHASE
        # =========================================================

        customers_no_purchase = list(
            Customer.objects
            .filter(
                sales__isnull=True
            )
            .values(
                "id",
                "name",
                "phone",
                "email",
            )
        )

        # =========================================================
        # 15. MEDICINES NEVER SOLD
        # =========================================================

        medicines_never_sold = list(
            Medicine.objects
            .filter(
                sale_items__isnull=True
            )
            .values(
                "id",
                "name",
                "generic_name",
            )
        )

        # =========================================================
        # 16. SUPPLIERS WITH NO PURCHASE
        # =========================================================

        suppliers_no_purchase = list(
            Supplier.objects
            .filter(
                purchases__isnull=True
            )
            .values(
                "id",
                "name",
                "phone",
                "email",
            )
        )

        # =========================================================
        # 17. AVERAGE SELLING PRICE BY CATEGORY
        # =========================================================

        average_price_by_category = list(
            Category.objects
            .annotate(
                average_selling_price=Avg(
                    "medicines__pc_price"
                )
            )
            .values(
                "id",
                "name",
                "average_selling_price",
            )
            .order_by("name")
        )

        # =========================================================
        # 18. STOCK VALUE OF EACH MEDICINE
        # =========================================================

        stock_value_per_medicine = list(
            Inventory.objects
            .select_related("medicine")
            .annotate(
                stock_value=ExpressionWrapper(
                    F("current_stock")
                    * F("medicine__cost_price"),
                    output_field=DecimalField(
                        max_digits=15,
                        decimal_places=2,
                    ),
                )
            )
            .values(
                "medicine_id",
                "medicine__name",
                "current_stock",
                "medicine__cost_price",
                "stock_value",
            )
            .order_by("-stock_value")
        )

        # =========================================================
        # 19. TOTAL STOCK VALUE
        # =========================================================

        total_stock_value = (
            Inventory.objects
            .annotate(
                stock_value=ExpressionWrapper(
                    F("current_stock")
                    * F("medicine__cost_price"),
                    output_field=DecimalField(
                        max_digits=15,
                        decimal_places=2,
                    ),
                )
            )
            .aggregate(
                total=Coalesce(
                    Sum("stock_value"),
                    Decimal("0.00"),
                )
            )["total"]
        )

        # =========================================================
        # 20. MOST FREQUENTLY PURCHASED MEDICINE
        #     BY EACH CUSTOMER
        # =========================================================

        customer_most_purchased = []

        customers = Customer.objects.all()

        for customer in customers:

            medicine_data = (
                SaleItem.objects
                .filter(
                    sale__customer=customer
                )
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

            if medicine_data:
                customer_most_purchased.append(
                    {
                        "customer_id":
                            customer.id,
                        "customer_name":
                            customer.name,
                        "medicine_id":
                            medicine_data[
                                "medicine_id"
                            ],
                        "medicine_name":
                            medicine_data[
                                "medicine__name"
                            ],
                        "total_quantity":
                            medicine_data[
                                "total_quantity"
                            ],
                    }
                )

        return Response(
            {
                "top_5_best_selling_medicines":
                    top_5_medicines,

                "supplier_with_highest_number_of_medicines":
                    supplier_highest_medicines,

                "customers_total_purchase_greater_than_10000":
                    customers_over_10000,

                "total_revenue":
                    total_revenue,

                "total_purchase_cost":
                    total_purchase_cost,

                "sales_minus_purchase_cost":
                    profit_difference,

                "low_stock_and_near_expiry":
                    low_stock_near_expiry,

                "customer_who_spent_the_most":
                    highest_spending_customer,

                "payment_method_highest_sales":
                    highest_payment_method,

                "monthly_sales_totals":
                    monthly_sales,

                "monthly_purchase_totals":
                    monthly_purchases,

                "medicines_sold_by_each_pharmacist":
                    medicines_by_pharmacist,

                "sales_by_each_pharmacist":
                    sales_by_pharmacist,

                "customers_with_no_purchase":
                    customers_no_purchase,

                "medicines_never_sold":
                    medicines_never_sold,

                "suppliers_with_no_purchase":
                    suppliers_no_purchase,

                "average_selling_price_by_category":
                    average_price_by_category,

                "stock_value_per_medicine":
                    stock_value_per_medicine,

                "total_pharmacy_stock_value":
                    total_stock_value,

                "most_frequently_purchased_by_customer":
                    customer_most_purchased,
            }
        )