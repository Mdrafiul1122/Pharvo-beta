from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from tests.helpers import auth_client, make_customer, make_staff, make_user


class CustomerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_staff("cust_staff")
        cls.clerk = make_user("cust_clerk")

    def test_crud_and_membership(self):
        client = auth_client(self.staff)
        response = client.post(
            "/api/customers/",
            {
                "name": "Alice",
                "phone": "555-1000",
                "email": "alice@example.com",
                "address": "1st Avenue",
                "membership_tier": "gold",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_member"])
        self.assertEqual(response.data["membership_tier"], "gold")
        default_response = client.post(
            "/api/customers/",
            {
                "name": "Bob",
                "phone": "555-2000",
                "email": "bob@example.com",
                "address": "2nd Avenue",
            },
            format="json",
        )
        self.assertFalse(default_response.data["is_member"])

    def test_validation(self):
        client = auth_client(self.staff)
        payloads = (
            {"name": "  ", "phone": "555-1", "email": "a@b.c", "address": "x"},
            {"name": "x", "phone": "  ", "email": "a@b.c", "address": "x"},
            {"name": "x", "phone": "555-1", "email": "  ", "address": "x"},
            {"name": "x", "phone": "555-1", "email": "a@b.c", "address": " "},
            {
                "name": "x",
                "phone": "555-1",
                "email": "a@b.c",
                "address": "x",
                "loyalty_points": -1,
            },
            {
                "name": "x",
                "phone": "555-1",
                "email": "a@b.c",
                "address": "x",
                "date_of_birth": (date.today() + timedelta(days=1)).isoformat(),
            },
        )
        for payload in payloads:
            self.assertEqual(
                client.post("/api/customers/", payload, format="json").status_code,
                400,
                msg=payload,
            )

    def test_permissions_and_search(self):
        self.assertEqual(
            auth_client(self.clerk)
            .post(
                "/api/customers/",
                {
                    "name": "x",
                    "phone": "555-3",
                    "email": "a@b.c",
                    "address": "x",
                },
                format="json",
            ).status_code,
            403,
        )
        self.assertEqual(APIClient().get("/api/customers/").status_code, 401)
        make_customer(name="Alice Search", phone="555-5000")
        data = auth_client(self.staff).get("/api/customers/?search=alice").data
        self.assertEqual(data[0]["name"], "Alice Search")