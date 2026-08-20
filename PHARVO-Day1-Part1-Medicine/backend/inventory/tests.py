from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from inventory.models import Category, Medicine


class MedicineAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="medicine_test", password="StrongPass123!"
        )
        self.client.force_authenticate(self.user)
        self.category = Category.objects.create(name="Pain Relief")
        self.url = reverse("medicine-list")

    def payload(self, **overrides):
        data = {
            "name": "Napa",
            "generic_name": "Paracetamol",
            "manufacturer": "Beximco",
            "category": self.category.id,
            "strength": "500 mg",
            "dosage_form": "TABLET",
            "pc_price": "1.00",
            "strip_price": "10.00",
            "box_price": "100.00",
            "minimum_stock": 20,
            "expiry_date": "2027-12-31",
            "is_active": True,
        }
        data.update(overrides)
        return data

    def test_create_medicine(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, 201)
        medicine = Medicine.objects.get()
        self.assertEqual(medicine.name, "Napa")
        self.assertEqual(str(medicine.pc_price), "1.00")
        self.assertFalse(hasattr(medicine, "barcode"))

    def test_reject_invalid_price_hierarchy(self):
        response = self.client.post(
            self.url,
            self.payload(strip_price="0.50"),
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("strip_price", response.data)

    def test_search_medicine(self):
        data = self.payload()
        Medicine.objects.create(
            category=self.category,
            name=data["name"],
            generic_name=data["generic_name"],
            manufacturer=data["manufacturer"],
            strength=data["strength"],
            dosage_form=data["dosage_form"],
            pc_price=data["pc_price"],
            strip_price=data["strip_price"],
            box_price=data["box_price"],
            minimum_stock=data["minimum_stock"],
            expiry_date=data["expiry_date"],
            is_active=data["is_active"],
        )
        response = self.client.get(f"{self.url}?search=Paracetamol")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

