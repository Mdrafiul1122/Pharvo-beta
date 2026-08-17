from datetime import date, timedelta
from threading import Thread

from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from sales.models import Sale, SalePayment
from tests.helpers import (
    auth_client,
    make_customer,
    make_product,
    make_staff,
)


def _checkout_payload(product_id, quantity, payments, **kwargs):
    payload = {
        "items": [{"product": product_id, "quantity": quantity}],
        "payments": payments,
    }
    payload.update(kwargs)
    return payload


class PosCheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_staff("pos_staff")
        cls.customer = make_customer(name="POS Customer", phone="555-4000")

    def test_checkout_happy_path(self):
        product = make_product(barcode="BC-POS1", stock_quantity=10, unit_price=100)
        client = auth_client(self.staff)
        response = client.post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id, 2, [{"method": "cash", "amount": "200.00"}],
                customer=self.customer.id,
            ),
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(float(response.data["payable_amount"]), 200.0)
        self.assertEqual(response.data["customer_name"], "POS Customer")
        self.assertEqual(SalePayment.objects.filter(sale=response.data["id"]).count(), 1)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 8)

    def test_split_payment(self):
        product = make_product(barcode="BC-POS2", stock_quantity=5, unit_price=100)
        response = auth_client(self.staff).post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id,
                2,
                [
                    {"method": "cash", "amount": "120.00"},
                    {"method": "card", "amount": "80.00"},
                ],
            ),
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["payment_method"], "cash")
        payments = list(
            SalePayment.objects.filter(sale=response.data["id"])
            .values_list("method", "amount")
        )
        self.assertEqual(len(payments), 2)

    def test_payment_mismatch_rejected(self):
        product = make_product(barcode="BC-POS3", stock_quantity=5, unit_price=100)
        response = auth_client(self.staff).post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id, 2, [{"method": "cash", "amount": "150.00"}]
            ),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 5)

    def test_sensitive_medicine_requires_approval(self):
        product = make_product(
            barcode="BC-POS4", stock_quantity=5, unit_price=100, is_sensitive=True
        )
        client = auth_client(self.staff)
        pending = client.post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id, 1, [{"method": "cash", "amount": "100.00"}]
            ),
            format="json",
        )
        self.assertEqual(pending.status_code, 200)
        self.assertTrue(pending.data["requires_approval"])
        self.assertEqual(Sale.objects.count(), 0)
        approved = client.post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id,
                1,
                [{"method": "cash", "amount": "100.00"}],
                approve_sensitive=True,
            ),
            format="json",
        )
        self.assertEqual(approved.status_code, 201)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 4)

    def test_expired_medicine_blocked(self):
        product = make_product(
            barcode="BC-POS5",
            stock_quantity=5,
            unit_price=100,
            expiry_date=date.today() - timedelta(days=3),
        )
        response = auth_client(self.staff).post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id, 1, [{"method": "cash", "amount": "100.00"}]
            ),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 5)

    def test_insufficient_stock_rollback(self):
        product = make_product(barcode="BC-POS6", stock_quantity=1, unit_price=100)
        response = auth_client(self.staff).post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id, 5, [{"method": "cash", "amount": "500.00"}]
            ),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 1)

    def test_requires_staff(self):
        from tests.helpers import make_user

        clerk = make_user("pos_clerk")
        product = make_product(barcode="BC-POS7", stock_quantity=5, unit_price=100)
        response = auth_client(clerk).post(
            "/api/pos/checkout/",
            _checkout_payload(
                product.id, 1, [{"method": "cash", "amount": "100.00"}]
            ),
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class ConcurrentCheckoutTest(TransactionTestCase):
    def test_concurrent_checkout_never_oversells(self):
        user = make_staff("conc_staff")
        product = make_product(barcode="BC-CONC", stock_quantity=1, unit_price=100)
        results = []

        def checkout():
            from django.db import connections

            try:
                client = APIClient()
                client.force_authenticate(user)
                response = client.post(
                    "/api/pos/checkout/",
                    _checkout_payload(
                        product.id, 1, [{"method": "cash", "amount": "100.00"}]
                    ),
                    format="json",
                )
                results.append(response.status_code)
            finally:
                connections.close_all()

        threads = [Thread(target=checkout) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=60)
        self.assertEqual(sorted(results), [201, 400])
        product.refresh_from_db()
        self.assertEqual(product.stock_quantity, 0)