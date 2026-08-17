from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, F, Sum
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsPharmacyStaff
from customers.models import Customer
from inventory.models import Product
from inventory.views import NEAR_EXPIRY_DAYS
from purchases.models import Purchase, PurchaseItem
from sales.models import Sale, SaleItem

DEFAULT_DAYS = 30
ZERO = Decimal("0.00")


def _parse_date(value, name):
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(
            {name: f"Invalid {name}. Expected format YYYY-MM-DD."}
        )


def _date_range(request):
    start = _parse_date(request.query_params.get("start_date"), "start_date")
    end = _parse_date(request.query_params.get("end_date"), "end_date")
    if start is None and end is None:
        end = date.today()
        start = end - timedelta(days=DEFAULT_DAYS)
    elif start is None:
        start = end - timedelta(days=DEFAULT_DAYS)
    elif end is None:
        end = date.today()
    if start > end:
        raise ValidationError(
            {"start_date": "start_date must not be after end_date."}
        )
    return start, end


class SalesReportView(APIView):
    permission_classes = [IsPharmacyStaff]

    def get(self, request):
        start, end = _date_range(request)
        sales = Sale.objects.filter(sale_date__range=(start, end))
        totals = sales.aggregate(
            total_revenue=Sum("payable_amount"),
            total_discount=Sum("discount"),
        )
        items_sold = (
            SaleItem.objects.filter(sale__sale_date__range=(start, end)).aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )
        daily_sales = (
            sales.values("sale_date")
            .annotate(sales_count=Count("id"), revenue=Sum("payable_amount"))
            .order_by("sale_date")
        )
        top_products = (
            SaleItem.objects.filter(sale__sale_date__range=(start, end))
            .values("product", "product__name", "product__barcode")
            .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("subtotal"))
            .order_by("-total_quantity")[:10]
        )
        return Response(
            {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "total_sales": sales.count(),
                "total_revenue": totals["total_revenue"] or ZERO,
                "total_discount": totals["total_discount"] or ZERO,
                "items_sold": items_sold,
                "daily_sales_summary": [
                    {
                        "sale_date": row["sale_date"],
                        "sales_count": row["sales_count"],
                        "revenue": row["revenue"] or ZERO,
                    }
                    for row in daily_sales
                ],
                "top_selling_products": [
                    {
                        "product": row["product"],
                        "product_name": row["product__name"],
                        "product_barcode": row["product__barcode"],
                        "total_quantity": row["total_quantity"],
                        "total_revenue": row["total_revenue"] or ZERO,
                    }
                    for row in top_products
                ],
            }
        )


class PurchasesReportView(APIView):
    permission_classes = [IsPharmacyStaff]

    def get(self, request):
        start, end = _date_range(request)
        purchases = Purchase.objects.filter(purchase_date__range=(start, end))
        totals = purchases.aggregate(
            total_purchase_amount=Sum("total_amount"),
            total_payable_amount=Sum("payable_amount"),
        )
        quantity_purchased = (
            PurchaseItem.objects.filter(
                purchase__purchase_date__range=(start, end)
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )
        supplier_stats = (
            purchases.values("supplier", "supplier__name")
            .annotate(
                purchase_count=Count("id", distinct=True),
                total_amount=Sum("total_amount"),
                payable_amount=Sum("payable_amount"),
            )
            .order_by("-payable_amount")
        )
        supplier_quantities = {
            row["purchase__supplier"]: row["total_quantity"]
            for row in PurchaseItem.objects.filter(
                purchase__purchase_date__range=(start, end)
            )
            .values("purchase__supplier")
            .annotate(total_quantity=Sum("quantity"))
        }
        return Response(
            {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "total_purchases": purchases.count(),
                "total_purchase_amount": totals["total_purchase_amount"] or ZERO,
                "total_payable_amount": totals["total_payable_amount"] or ZERO,
                "quantity_purchased": quantity_purchased,
                "supplier_wise_summary": [
                    {
                        "supplier": row["supplier"],
                        "supplier_name": row["supplier__name"],
                        "purchase_count": row["purchase_count"],
                        "total_amount": row["total_amount"] or ZERO,
                        "payable_amount": row["payable_amount"] or ZERO,
                        "total_quantity": supplier_quantities.get(
                            row["supplier"], 0
                        ),
                    }
                    for row in supplier_stats
                ],
            }
        )


class ProfitReportView(APIView):
    permission_classes = [IsPharmacyStaff]

    def get(self, request):
        start, end = _date_range(request)
        revenue = (
            Sale.objects.filter(sale_date__range=(start, end)).aggregate(
                total=Sum("payable_amount")
            )["total"]
            or ZERO
        )
        purchase_cost = (
            SaleItem.objects.filter(sale__sale_date__range=(start, end)).aggregate(
                total=Sum(F("quantity") * F("product__cost_price"))
            )["total"]
            or ZERO
        )
        profit = revenue - purchase_cost
        margin = (profit / revenue * 100) if revenue else ZERO
        return Response(
            {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "revenue": revenue,
                "purchase_cost": purchase_cost,
                "profit": profit,
                "profit_margin": margin,
            }
        )


class StockReportView(APIView):
    permission_classes = [IsPharmacyStaff]

    def get(self, request):
        today = date.today()
        window_end = today + timedelta(days=NEAR_EXPIRY_DAYS)
        stock_value = Product.objects.aggregate(
            retail_value=Sum(F("stock_quantity") * F("unit_price")),
            cost_value=Sum(F("stock_quantity") * F("cost_price")),
        )
        return Response(
            {
                "total_products": Product.objects.count(),
                "active_products": Product.objects.filter(is_active=True).count(),
                "low_stock_products": Product.objects.filter(
                    stock_quantity__gt=0,
                    stock_quantity__lte=F("reorder_level"),
                ).count(),
                "out_of_stock_products": Product.objects.filter(
                    stock_quantity__lte=0
                ).count(),
                "expired_products": Product.objects.filter(
                    expiry_date__lt=today
                ).count(),
                "near_expiry_products": Product.objects.filter(
                    expiry_date__gte=today, expiry_date__lte=window_end
                ).count(),
                "near_expiry_days": NEAR_EXPIRY_DAYS,
                "stock_value": {
                    "retail": stock_value["retail_value"] or ZERO,
                    "cost": stock_value["cost_value"] or ZERO,
                },
            }
        )


class CustomersReportView(APIView):
    permission_classes = [IsPharmacyStaff]

    def get(self, request):
        top_by_spending = (
            Customer.objects.annotate(total_spend=Sum("sales__payable_amount"))
            .filter(total_spend__isnull=False)
            .order_by("-total_spend")[:10]
        )
        top_by_count = (
            Customer.objects.annotate(purchase_count=Count("sales"))
            .filter(purchase_count__gt=0)
            .order_by("-purchase_count")[:10]
        )
        return Response(
            {
                "total_customers": Customer.objects.count(),
                "customers_with_purchases": (
                    Sale.objects.filter(customer__isnull=False)
                    .values("customer")
                    .distinct()
                    .count()
                ),
                "top_customers_by_spending": [
                    {
                        "id": customer.id,
                        "name": customer.name,
                        "phone": customer.phone,
                        "total_spend": customer.total_spend,
                    }
                    for customer in top_by_spending
                ],
                "top_customers_by_purchase_count": [
                    {
                        "id": customer.id,
                        "name": customer.name,
                        "phone": customer.phone,
                        "purchase_count": customer.purchase_count,
                    }
                    for customer in top_by_count
                ],
            }
        )
