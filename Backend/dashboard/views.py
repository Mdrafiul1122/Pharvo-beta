from datetime import date, timedelta
from decimal import Decimal

from django.db.models import F, Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsPharmacyStaff
from customers.models import Customer
from inventory.models import Product, Supplier
from inventory.views import NEAR_EXPIRY_DAYS
from purchases.models import Purchase
from sales.models import Sale, SaleItem
from sales.serializers import SaleSerializer

DEFAULT_DAYS = 30


def _parse_days(request):
    days = request.query_params.get("days")
    try:
        days = int(days)
    except (TypeError, ValueError):
        return DEFAULT_DAYS
    return days if days > 0 else DEFAULT_DAYS


class DashboardView(APIView):
    permission_classes = [IsPharmacyStaff]

    def get(self, request):
        days = _parse_days(request)
        today = date.today()
        start_date = today - timedelta(days=days)
        window_end = today + timedelta(days=NEAR_EXPIRY_DAYS)

        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        low_stock_count = Product.objects.filter(
            stock_quantity__lte=F("reorder_level")
        ).count()
        expired_count = Product.objects.filter(expiry_date__lt=today).count()
        near_expiry_count = Product.objects.filter(
            expiry_date__gte=today, expiry_date__lte=window_end
        ).count()

        total_sales = Sale.objects.count()
        total_revenue = (
            Sale.objects.aggregate(total=Sum("payable_amount"))["total"]
            or Decimal("0.00")
        )
        total_purchases = Purchase.objects.count()
        total_purchase_amount = (
            Purchase.objects.aggregate(total=Sum("payable_amount"))["total"]
            or Decimal("0.00")
        )

        recent_sales = (
            Sale.objects.select_related("customer", "user")
            .prefetch_related("items__product")
            .order_by("-sale_date", "-created_at")[:5]
        )

        top_selling_products = [
            {
                "product": item["product"],
                "product_name": item["product__name"],
                "product_barcode": item["product__barcode"],
                "total_quantity": item["total_quantity"],
            }
            for item in (
                SaleItem.objects.values(
                    "product", "product__name", "product__barcode"
                )
                .annotate(total_quantity=Sum("quantity"))
                .order_by("-total_quantity")[:5]
            )
        ]

        period_sales = Sale.objects.filter(sale_date__gte=start_date)
        period_revenue = (
            period_sales.aggregate(total=Sum("payable_amount"))["total"]
            or Decimal("0.00")
        )
        period_items_sold = (
            SaleItem.objects.filter(sale__sale_date__gte=start_date).aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        return Response(
            {
                "total_products": total_products,
                "active_products": active_products,
                "total_customers": Customer.objects.count(),
                "total_suppliers": Supplier.objects.count(),
                "total_sales": total_sales,
                "total_revenue": total_revenue,
                "total_purchases": total_purchases,
                "total_purchase_amount": total_purchase_amount,
                "low_stock_count": low_stock_count,
                "expired_count": expired_count,
                "near_expiry_count": near_expiry_count,
                "recent_sales": SaleSerializer(recent_sales, many=True).data,
                "top_selling_products": top_selling_products,
                "sales_summary": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": today.isoformat(),
                    "sales_count": period_sales.count(),
                    "revenue": period_revenue,
                    "items_sold": period_items_sold,
                },
            }
        )
