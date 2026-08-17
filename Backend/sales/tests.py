from datetime import date

from django.test import TestCase

from sales.models import Sale
from tests.helpers import auth_client, make_customer, make_product, make_staff, make_user


def _sale_payload(product_id, quantity, unit_price, invoice, discount="0.00"):
    return {
        "invoice_number": invoice,
        "items": [
            {
                "product": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        ],
        "discount": discount,
        "sale_date": date.today().isoformat(),
    }


class SaleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_staff("sale_staff")
        cls.clerk = make_user("sale_clerk")
        cls.customer = make_customer(name="Sale Customer", phone="555-3000")
        cls.product = make_product(barcode="BC-SALE", stock_quantity=10)

    def test_create_sale_totals_and_stock(self):
        response = auth_client(self.staff).post(
            "/api/sales/",
            _sale_payload(self.product.id, 2, "100.00", "SALE-1", "5.00"),
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(float(response.data["total_amount"]), 200.0)
        self.assertEqual(float(response.data["payable_amount"]), 195.0)
        self.assertEqual(response.data["user_username"], self.staff.username)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_non_staff_can_read_not_write(self):
        client = auth_client(self.clerk)
        self.assertEqual(client.get("/api/sales/").status_code, 200)
        response = client.post(
            "/api/sales/",
            _sale_payload(self.product.id, 1, "100.00", "SALE-DENY"),
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_update_sale_restores_and_deducts(self):
        client = auth_client(self.staff)
        response = client.post(
            "/api/sales/",
            _sale_payload(self.product.id, 2, "100.00", "SALE-2"),
            format="json",
        )
        sale_id = response.data["id"]
        client.patch(
            f"/api/sales/{sale_id}/",
            {
                "items": [
                    {
                        "product": self.product.id,
                        "quantity": 3,
                        "unit_price": "100.00",
                    }
                ]
            },
            format="json",
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

    def test_delete_sale_restores_stock(self):
        client = auth_client(self.staff)
        response = client.post(
            "/api/sales/",
            _sale_payload(self.product.id, 4, "100.00", "SALE-3"),
            format="json",
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 6)
        self.assertEqual(
            client.delete(f"/api/sales/{response.data['id']}/").status_code, 204
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)

    def test_validation_empty_items_and_discount(self):
        client = auth_client(self.staff)
        empty = {
            "invoice_number": "SALE-EMPTY",
            "items": [],
            "sale_date": date.today().isoformat(),
        }
        self.assertEqual(
            client.post("/api/sales/", empty, format="json").status_code, 400
        )
        response = client.post(
            "/api/sales/",
            _sale_payload(self.product.id, 2, "100.00", "SALE-DISC", "500.00"),
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_insufficient_stock_rolls_back(self):
        product = make_product(barcode="BC-LOW", stock_quantity=1)
        response = auth_client(self.staff).post(
            "/api/sales/",
            _sale_payload(product.id, 5, "100.00", "SALE-INSUF"),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Sale.objects.filter(invoice_number="SALE-INSUF").count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 1)