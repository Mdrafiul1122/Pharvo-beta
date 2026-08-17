from datetime import date, timedelta

from django.test import TestCase

from purchases.models import Purchase, PurchaseItem
from sales.models import Sale, SaleItem
from tests.helpers import (
    auth_client,
    make_customer,
    make_product,
    make_staff,
    make_supplier,
)


class ReportsDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_staff("rep_staff")
        cls.supplier = make_supplier("ReportSource")
        cls.customer = make_customer(name="Report Customer", phone="555-9000")
        cls.customer2 = make_customer(name="Second Customer", phone="555-9001")
        cls.low = make_product(barcode="R-LOW", stock_quantity=5, reorder_level=10,
                               unit_price=15, cost_price=10,
                               expiry_date=date.today() + timedelta(days=10))
        cls.out = make_product(barcode="R-OUT", stock_quantity=0,
                               unit_price=30, cost_price=20)
        cls.expired = make_product(barcode="R-EXP", stock_quantity=50,
                                   unit_price=8, cost_price=5,
                                   expiry_date=date.today() - timedelta(days=5))
        cls.inactive = make_product(barcode="R-INAC", stock_quantity=10,
                                    reorder_level=2, is_active=False)
        cls.today = date.today()

        cls.sale_in = Sale.objects.create(
            invoice_number="R-S1", customer=cls.customer, user=cls.staff,
            total_amount=30, discount=5, payable_amount=25,
            sale_date=cls.today,
        )
        SaleItem.objects.create(
            sale=cls.sale_in, product=cls.low, quantity=2,
            unit_price=15, subtotal=30,
        )
        cls.sale_in2 = Sale.objects.create(
            invoice_number="R-S2", customer=cls.customer2, user=cls.staff,
            total_amount=90, discount=0, payable_amount=90,
            sale_date=cls.today - timedelta(days=5),
        )
        SaleItem.objects.create(
            sale=cls.sale_in2, product=cls.out, quantity=3,
            unit_price=30, subtotal=90,
        )
        cls.sale_out = Sale.objects.create(
            invoice_number="R-S3", customer=None, user=cls.staff,
            total_amount=8, discount=0, payable_amount=8,
            sale_date=cls.today - timedelta(days=40),
        )
        SaleItem.objects.create(
            sale=cls.sale_out, product=cls.expired, quantity=1,
            unit_price=8, subtotal=8,
        )
        cls.purchase_in = Purchase.objects.create(
            invoice_number="R-P1", supplier=cls.supplier, user=cls.staff,
            total_amount=80, discount=5, payable_amount=75,
            purchase_date=cls.today,
        )
        PurchaseItem.objects.create(
            purchase=cls.purchase_in, product=cls.low, quantity=10,
            unit_price=8, subtotal=80,
        )

    def setUp(self):
        self.client = auth_client(self.staff)

    def test_sales_report_totals_and_daily_summary(self):
        data = self.client.get("/api/reports/sales/").data
        self.assertEqual(data["total_sales"], 2)
        self.assertEqual(float(data["total_revenue"]), 115.0)
        self.assertEqual(float(data["total_discount"]), 5.0)
        self.assertEqual(data["items_sold"], 5)
        self.assertEqual(len(data["daily_sales_summary"]), 2)
        self.assertEqual(data["top_selling_products"][0]["product_name"], self.out.name)

    def test_sales_date_filtering(self):
        start = (self.today - timedelta(days=2)).isoformat()
        end = self.today.isoformat()
        data = self.client.get(
            f"/api/reports/sales/?start_date={start}&end_date={end}"
        ).data
        self.assertEqual(data["total_sales"], 1)
        self.assertEqual(float(data["total_revenue"]), 25.0)
        self.assertEqual(data["items_sold"], 2)

    def test_invalid_dates_return_400(self):
        self.assertEqual(
            self.client.get("/api/reports/sales/?start_date=bad").status_code, 400
        )
        self.assertEqual(
            self.client.get(
                "/api/reports/sales/?start_date=2026-01-10&end_date=2026-01-01"
            ).status_code,
            400,
        )

    def test_purchases_report(self):
        data = self.client.get("/api/reports/purchases/").data
        self.assertEqual(data["total_purchases"], 1)
        self.assertEqual(float(data["total_purchase_amount"]), 80.0)
        self.assertEqual(float(data["total_payable_amount"]), 75.0)
        self.assertEqual(data["quantity_purchased"], 10)
        summary = data["supplier_wise_summary"][0]
        self.assertEqual(summary["supplier_name"], "ReportSource")
        self.assertEqual(summary["total_quantity"], 10)
        self.assertEqual(float(summary["payable_amount"]), 75.0)

    def test_purchases_date_filtering(self):
        data = self.client.get(
            "/api/reports/purchases/?start_date=2020-01-01&end_date=2020-01-31"
        ).data
        self.assertEqual(data["total_purchases"], 0)

    def test_profit_report(self):
        data = self.client.get("/api/reports/profit/").data
        self.assertEqual(float(data["revenue"]), 115.0)
        self.assertEqual(float(data["purchase_cost"]), 80.0)
        self.assertEqual(float(data["profit"]), 35.0)
        self.assertEqual(round(float(data["profit_margin"]), 2), 30.43)

    def test_stock_report(self):
        data = self.client.get("/api/reports/stock/").data
        self.assertEqual(data["total_products"], 4)
        self.assertEqual(data["active_products"], 3)
        self.assertEqual(data["low_stock_products"], 1)
        self.assertEqual(data["out_of_stock_products"], 1)
        self.assertEqual(data["expired_products"], 1)
        self.assertEqual(data["near_expiry_products"], 1)
        self.assertEqual(
            float(data["stock_value"]["retail"]),
            5 * 15 + 0 + 50 * 8 + 10 * 100,
        )
        self.assertEqual(
            float(data["stock_value"]["cost"]),
            5 * 10 + 0 + 50 * 5 + 10 * 60,
        )

    def test_customers_report(self):
        data = self.client.get("/api/reports/customers/").data
        self.assertEqual(data["total_customers"], 2)
        self.assertEqual(data["customers_with_purchases"], 2)
        self.assertEqual(
            data["top_customers_by_spending"][0]["name"], "Second Customer"
        )
        self.assertEqual(
            float(data["top_customers_by_spending"][0]["total_spend"]), 90.0
        )


class EmptyDatabaseReportsTestCase(TestCase):
    def setUp(self):
        self.client = auth_client(make_staff("empty_rep_staff"))

    def test_empty_database_returns_safe_values(self):
        sales = self.client.get("/api/reports/sales/").data
        self.assertEqual(sales["total_sales"], 0)
        self.assertEqual(float(sales["total_revenue"]), 0.0)
        self.assertEqual(sales["daily_sales_summary"], [])
        profit = self.client.get("/api/reports/profit/").data
        self.assertEqual(float(profit["profit"]), 0.0)
        self.assertEqual(float(profit["profit_margin"]), 0.0)
        stock = self.client.get("/api/reports/stock/").data
        self.assertEqual(stock["total_products"], 0)
        self.assertEqual(float(stock["stock_value"]["retail"]), 0.0)
        customers = self.client.get("/api/reports/customers/").data
        self.assertEqual(customers["total_customers"], 0)
        self.assertEqual(customers["top_customers_by_spending"], [])