from django.test import TestCase
from rest_framework.test import APIClient

from tests.helpers import auth_client, make_staff, make_user

from .models import User


def signup(client, **overrides):
    payload = {
        "full_name": "Jane Pharmacist",
        "email": "jane@pharvo.test",
        "password": "secret123",
        "confirm_password": "secret123",
        "role": "pharmacist",
    }
    payload.update(overrides)
    return client.post("/api/auth/signup/", payload, format="json")


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
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["role"], User.Role.PHARMACIST)

    def test_login_access_token_contains_role_claim(self):
        login = APIClient().post(
            "/api/auth/login/",
            {"username": "authuser", "password": "secret123"},
            format="json",
        )
        from rest_framework_simplejwt.tokens import AccessToken

        payload = AccessToken(login.data["access"]).payload
        self.assertEqual(payload["role"], User.Role.PHARMACIST)

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


class SignupTests(TestCase):
    def test_signup_creates_pharmacist(self):
        response = signup(APIClient())
        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user = User.objects.get(email="jane@pharvo.test")
        self.assertEqual(user.role, User.Role.PHARMACIST)
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Pharmacist")
        self.assertEqual(response.data["user"]["role"], User.Role.PHARMACIST)

    def test_signup_creates_customer(self):
        response = signup(
            APIClient(),
            full_name="John Customer",
            email="john@pharvo.test",
            role="customer",
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="john@pharvo.test")
        self.assertEqual(user.role, User.Role.CUSTOMER)

    def test_signup_rejects_admin_role(self):
        response = signup(APIClient(), role="admin")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="jane@pharvo.test").exists())

    def test_signup_rejects_password_mismatch(self):
        response = signup(APIClient(), confirm_password="different")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="jane@pharvo.test").exists())

    def test_signup_rejects_duplicate_email(self):
        signup(APIClient())
        response = signup(APIClient(), full_name="Copy Cat")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(email="jane@pharvo.test").count(), 1)


class MeEndpointTests(TestCase):
    def test_me_returns_current_user_with_role(self):
        client = auth_client(make_user("me_user", password="secret123"))
        response = client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "me_user")
        self.assertEqual(response.data["role"], User.Role.PHARMACIST)

    def test_me_requires_authentication(self):
        response = APIClient().get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)


class RoleEnforcementTests(TestCase):
    def test_customer_denied_pharmacy_apis(self):
        customer = User.objects.create_user(
            username="cust_user",
            email="cust@pharvo.test",
            password="secret123",
            role=User.Role.CUSTOMER,
        )
        client = auth_client(customer)
        for url in (
            "/api/inventory/products/",
            "/api/customers/",
            "/api/sales/",
            "/api/dashboard/",
            "/api/reports/sales/",
            "/api/notifications/",
        ):
            self.assertEqual(client.get(url).status_code, 403, msg=url)

    def test_customer_can_read_own_profile(self):
        customer = User.objects.create_user(
            username="cust2",
            email="cust2@pharvo.test",
            password="secret123",
            role=User.Role.CUSTOMER,
        )
        client = auth_client(customer)
        self.assertEqual(client.get("/api/auth/me/").status_code, 200)

    def test_pharmacist_can_read_pharmacy_apis(self):
        client = auth_client(make_user("pharm_user", password="secret123"))
        self.assertEqual(client.get("/api/inventory/products/").status_code, 200)