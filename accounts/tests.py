from django.test import TestCase
from rest_framework.test import APIClient

from tests.helpers import auth_client, make_staff, make_user


class JWTAuthTests(TestCase):
    def setUp(self):
        self.user = make_user("authuser", password="secret123")

    def test_valid_login(self):
        response = APIClient().post(
            "/api/auth/login/",
            {"username": "authuser", "password": "secret123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_login(self):
        response = APIClient().post(
            "/api/auth/login/",
            {"username": "authuser", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_api_returns_401(self):
        response = APIClient().get("/api/inventory/products/")
        self.assertEqual(response.status_code, 401)

    def test_access_token_grants_access(self):
        login = APIClient().post(
            "/api/auth/login/",
            {"username": "authuser", "password": "secret123"},
            format="json",
        )
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        response = client.get("/api/inventory/products/")
        self.assertEqual(response.status_code, 200)

    def test_read_endpoints_smoke(self):
        staff = make_staff("smoke_staff")
        client = auth_client(staff)
        for url in (
            "/api/inventory/products/",
            "/api/customers/",
            "/api/sales/",
            "/api/purchases/",
            "/api/crm/customers/",
            "/api/dashboard/",
            "/api/reports/sales/",
            "/api/notifications/",
        ):
            self.assertEqual(client.get(url).status_code, 200, msg=url)
        self.assertEqual(client.get("/api/pos/checkout/").status_code, 405)