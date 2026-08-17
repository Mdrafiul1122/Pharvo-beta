from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from customers.models import Customer
from inventory.models import Category, MedicineGroup, Product, Supplier


def make_user(username="tester", password="testpass123", is_staff=False):
    user = get_user_model().objects.create_user(
        username=username, password=password
    )
    if is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
    return user


def make_staff(username="staff_user"):
    return make_user(username=username, is_staff=True)


def make_category(name="General"):
    return Category.objects.create(name=name)


def make_supplier(name="Supplier Co"):
    return Supplier.objects.create(name=name)


def make_group(name="Antibiotics"):
    return MedicineGroup.objects.create(name=name)


def make_product(barcode="bc-1", **kwargs):
    defaults = {
        "name": f"Product {barcode}",
        "barcode": barcode,
        "unit_price": 100,
        "cost_price": 60,
        "stock_quantity": 50,
        "reorder_level": 10,
    }
    defaults.update(kwargs)
    return Product.objects.create(**defaults)


def make_customer(name="Customer", phone="555-0100", **kwargs):
    defaults = {
        "name": name,
        "phone": phone,
        "email": f"{name.lower().replace(' ', '_')}@example.com",
        "address": "123 Main St",
    }
    defaults.update(kwargs)
    return Customer.objects.create(**defaults)


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client