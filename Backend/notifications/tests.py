from datetime import date, timedelta

from django.test import TestCase

from inventory.models import Product
from notifications.models import Notification
from tests.helpers import auth_client, make_product, make_staff


class NotificationAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_staff("notif_staff")
        today = date.today()
        make_product(barcode="N-LOW", stock_quantity=5, reorder_level=10)
        make_product(barcode="N-OUT", stock_quantity=0, reorder_level=5)
        make_product(
            barcode="N-EXP", stock_quantity=20, reorder_level=2,
            expiry_date=today - timedelta(days=5),
        )
        make_product(
            barcode="N-NEAR", stock_quantity=20, reorder_level=2,
            expiry_date=today + timedelta(days=10),
        )
        make_product(
            barcode="N-OK", stock_quantity=50, reorder_level=5,
            expiry_date=today + timedelta(days=100),
        )
        make_product(
            barcode="N-INAC", stock_quantity=0, reorder_level=5, is_active=False
        )

    def setUp(self):
        self.client = auth_client(self.user)

    def test_authentication_required(self):
        from rest_framework.test import APIClient

        anon = APIClient()
        self.assertEqual(anon.get("/api/notifications/").status_code, 401)
        self.assertEqual(
            anon.get("/api/notifications/unread-count/").status_code, 401
        )
        self.assertEqual(
            anon.post("/api/notifications/mark-all-read/").status_code, 401
        )

    def test_alert_generation_and_deduplication(self):
        self.assertEqual(Notification.objects.count(), 0)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.objects.count(), 4)
        self.client.get("/api/notifications/")
        self.assertEqual(Notification.objects.count(), 4)
        types = {row["type"] for row in response.data}
        self.assertEqual(
            types, {"low_stock", "out_of_stock", "expired", "near_expiry"}
        )
        severities = {row["severity"] for row in response.data}
        self.assertEqual(severities, {"warning", "critical"})

    def test_alert_types(self):
        expected = {
            "low_stock": ("Product N-LOW", "warning"),
            "out_of_stock": ("Product N-OUT", "critical"),
            "expired": ("Product N-EXP", "critical"),
            "near_expiry": ("Product N-NEAR", "warning"),
        }
        for alert_type, (name, severity) in expected.items():
            data = self.client.get(f"/api/notifications/?type={alert_type}").data
            self.assertEqual(len(data), 1, msg=alert_type)
            self.assertEqual(data[0]["product_name"], name, msg=alert_type)
            self.assertEqual(data[0]["severity"], severity, msg=alert_type)

    def test_changed_status_creates_alert_and_stale_resolves(self):
        self.client.get("/api/notifications/")
        low = Product.objects.get(barcode="N-LOW")
        Product.objects.filter(pk=low.pk).update(stock_quantity=3)
        self.client.get("/api/notifications/")
        self.assertEqual(Notification.objects.count(), 5)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 4)
        self.assertTrue(
            Notification.objects.filter(
                type="low_stock", product=low, is_read=False
            ).exists()
        )

    def test_unread_count(self):
        response = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["unread_count"], 4)

    def test_mark_single_read(self):
        notification = self.client.get("/api/notifications/").data[0]
        response = self.client.patch(
            f"/api/notifications/{notification['id']}/read/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_read"])
        self.assertEqual(
            self.client.get("/api/notifications/unread-count/").data[
                "unread_count"
            ],
            3,
        )

    def test_mark_all_read(self):
        self.client.get("/api/notifications/")
        response = self.client.post("/api/notifications/mark-all-read/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["marked_read"], 4)
        self.assertEqual(
            self.client.get("/api/notifications/unread-count/").data[
                "unread_count"
            ],
            0,
        )

    def test_filters(self):
        self.client.get("/api/notifications/")
        self.assertEqual(
            len(self.client.get("/api/notifications/?is_read=false").data), 4
        )
        self.assertEqual(
            len(self.client.get("/api/notifications/?severity=critical").data), 2
        )
        self.assertEqual(
            len(self.client.get("/api/notifications/?type=low_stock").data), 1
        )
        self.assertEqual(
            len(self.client.get("/api/notifications/?severity=info").data), 0
        )

    def test_related_endpoints_still_work(self):
        self.client.get("/api/notifications/")
        for url in (
            "/api/dashboard/",
            "/api/reports/sales/",
            "/api/inventory/products/",
            "/api/sales/",
        ):
            self.assertEqual(self.client.get(url).status_code, 200, msg=url)