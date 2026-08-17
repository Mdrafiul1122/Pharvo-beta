from datetime import date, timedelta

from django.test import TestCase

from crm.models import Reminder
from sales.models import Sale, SaleItem, SalePayment
from tests.helpers import (
    auth_client,
    make_customer,
    make_product,
    make_staff,
    make_user,
)


class CRMTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_staff("crm_staff")
        cls.user = make_user("crm_user")
        cls.customer = make_customer(name="Alice CRM", phone="555-7000")
        cls.product = make_product(barcode="BC-CRM")
        cls.sale = Sale.objects.create(
            invoice_number="CRM-1",
            customer=cls.customer,
            user=cls.user,
            total_amount=150,
            discount=0,
            payable_amount=150,
            sale_date=date.today(),
        )
        SaleItem.objects.create(
            sale=cls.sale,
            product=cls.product,
            quantity=3,
            unit_price=50,
            subtotal=150,
        )
        SalePayment.objects.create(sale=cls.sale, method="cash", amount=90)
        SalePayment.objects.create(sale=cls.sale, method="card", amount=60)

    def test_crm_summary(self):
        client = auth_client(self.staff)
        data = client.get(
            f"/api/crm/customers/{self.customer.id}/summary/"
        ).data
        self.assertEqual(data["total_purchases"], 1)
        self.assertEqual(float(data["total_spending"]), 150.0)
        self.assertEqual(len(data["recent_purchases"]), 1)
        self.assertEqual(len(data["frequently_purchased_products"]), 1)
        self.assertEqual(
            data["frequently_purchased_products"][0]["total_quantity"], 3
        )

    def test_crm_purchase_history(self):
        data = auth_client(self.staff).get(
            f"/api/crm/customers/{self.customer.id}/purchases/"
        ).data
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]["payments"]), 2)
        self.assertEqual(float(data[0]["payable_amount"]), 150.0)

    def test_reminders_crud_and_filters(self):
        client = auth_client(self.staff)
        response = client.post(
            "/api/crm/reminders/",
            {
                "customer": self.customer.id,
                "product": self.product.id,
                "title": "Take with food",
                "reminder_time": (
                    date.today() + timedelta(days=1)
                ).strftime("%Y-%m-%dT12:00:00Z"),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        reminders = client.get(
            f"/api/crm/reminders/?customer={self.customer.id}"
        ).data
        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0]["product_name"], self.product.name)
        reminder_id = reminders[0]["id"]
        client.patch(
            f"/api/crm/reminders/{reminder_id}/", {"is_active": False}
        )
        self.assertFalse(
            Reminder.objects.get(pk=reminder_id).is_active
        )
        self.assertEqual(
            len(client.get("/api/crm/reminders/?active=false").data), 1
        )