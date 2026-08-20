from datetime import date, timedelta
from decimal import Decimal
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from customers.models import Customer
from inventory.models import (
    Category,
    Supplier,
    Medicine,
    Inventory,
    InventoryTransaction,
)
from purchases.models import Purchase, PurchaseItem
from sales.models import Sale, SaleItem


class Command(BaseCommand):
    help = "Seeds the database with sample pharmacy data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        random.seed(42)
        today = date.today()

        # ---------------------------------------------------------
        # USER
        # ---------------------------------------------------------
        user, user_created = User.objects.get_or_create(
            username="admin",
            defaults={
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if user_created:
            user.set_password("admin123")
            user.save()

        # ---------------------------------------------------------
        # CATEGORIES
        # ---------------------------------------------------------
        categories = [
            "Antibiotics",
            "Painkillers",
            "Vitamins & Supplements",
            "Cold & Flu",
            "Allergy",
            "Digestive Health",
            "Blood Pressure",
            "Diabetes",
            "First Aid",
            "Skincare",
        ]

        for name in categories:
            Category.objects.get_or_create(name=name)

        cat_map = {
            category.name: category
            for category in Category.objects.all()
        }

        # ---------------------------------------------------------
        # SUPPLIERS
        # ---------------------------------------------------------
        suppliers = [
            (
                "PharmaCure Ltd",
                "Ravi Sharma",
                "+8801712345601",
            ),
            (
                "MediSource Inc",
                "Sadia Rahman",
                "+8801712345602",
            ),
            (
                "HealthFirst Distributors",
                "Kamal Hossain",
                "+8801712345603",
            ),
            (
                "BioGen Pharmaceuticals",
                "Nusrat Jahan",
                "+8801712345604",
            ),
            (
                "CarePlus Medical",
                "Tanvir Ahmed",
                "+8801712345605",
            ),
        ]

        for name, contact, phone in suppliers:
            Supplier.objects.update_or_create(
                name=name,
                defaults={
                    "contact_person": contact,
                    "phone": phone,
                },
            )

        suppliers_list = list(Supplier.objects.all())

        # ---------------------------------------------------------
        # MEDICINES
        #
        # Structure:
        # name
        # generic_name
        # manufacturer
        # category
        # strength
        # dosage_form
        # pc_price
        # strip_price
        # box_price
        # purchase_price
        # opening_stock
        # minimum_stock
        # ---------------------------------------------------------
        medicines_data = [
            (
                "Amoxicillin",
                "Amoxicillin",
                "PharmaCure Ltd",
                "Antibiotics",
                "500mg",
                "CAPSULE",
                12,
                120,
                1200,
                8,
                500,
                50,
            ),
            (
                "Ciprofloxacin",
                "Ciprofloxacin",
                "MediSource Inc",
                "Antibiotics",
                "250mg",
                "TABLET",
                9,
                90,
                900,
                6,
                300,
                30,
            ),
            (
                "Azithromycin",
                "Azithromycin",
                "BioGen Pharmaceuticals",
                "Antibiotics",
                "500mg",
                "TABLET",
                25,
                75,
                750,
                18,
                200,
                20,
            ),
            (
                "Paracetamol",
                "Paracetamol",
                "HealthFirst Distributors",
                "Painkillers",
                "500mg",
                "TABLET",
                2,
                20,
                200,
                1,
                1000,
                100,
            ),
            (
                "Ibuprofen",
                "Ibuprofen",
                "PharmaCure Ltd",
                "Painkillers",
                "400mg",
                "TABLET",
                5,
                50,
                500,
                3,
                800,
                80,
            ),
            (
                "Naproxen",
                "Naproxen",
                "CarePlus Medical",
                "Painkillers",
                "250mg",
                "TABLET",
                8,
                80,
                800,
                5,
                400,
                40,
            ),
            (
                "Vitamin C",
                "Ascorbic Acid",
                "HealthFirst Distributors",
                "Vitamins & Supplements",
                "500mg",
                "TABLET",
                4,
                40,
                400,
                3,
                600,
                60,
            ),
            (
                "Vitamin D3",
                "Cholecalciferol",
                "BioGen Pharmaceuticals",
                "Vitamins & Supplements",
                "1000IU",
                "TABLET",
                6,
                60,
                600,
                4,
                500,
                50,
            ),
            (
                "Calcium Plus D",
                "Calcium + Vitamin D",
                "CarePlus Medical",
                "Vitamins & Supplements",
                "500mg",
                "TABLET",
                10,
                100,
                1000,
                7,
                350,
                35,
            ),
            (
                "Multivitamin",
                "Multivitamin",
                "MediSource Inc",
                "Vitamins & Supplements",
                "1 tablet",
                "TABLET",
                12,
                120,
                1200,
                8,
                400,
                40,
            ),
            (
                "Cetirizine",
                "Cetirizine Hydrochloride",
                "PharmaCure Ltd",
                "Allergy",
                "10mg",
                "TABLET",
                3,
                30,
                300,
                2,
                700,
                70,
            ),
            (
                "Loratadine",
                "Loratadine",
                "HealthFirst Distributors",
                "Allergy",
                "10mg",
                "TABLET",
                5,
                50,
                500,
                3,
                500,
                50,
            ),
            (
                "Omeprazole",
                "Omeprazole",
                "MediSource Inc",
                "Digestive Health",
                "20mg",
                "CAPSULE",
                7,
                70,
                700,
                4,
                450,
                45,
            ),
            (
                "Pantoprazole",
                "Pantoprazole",
                "BioGen Pharmaceuticals",
                "Digestive Health",
                "20mg",
                "TABLET",
                6,
                60,
                600,
                4,
                600,
                60,
            ),
            (
                "Amlodipine",
                "Amlodipine",
                "CarePlus Medical",
                "Blood Pressure",
                "5mg",
                "TABLET",
                5,
                50,
                500,
                3,
                400,
                40,
            ),
            (
                "Losartan",
                "Losartan Potassium",
                "PharmaCure Ltd",
                "Blood Pressure",
                "50mg",
                "TABLET",
                7,
                70,
                700,
                5,
                350,
                35,
            ),
            (
                "Metformin",
                "Metformin Hydrochloride",
                "HealthFirst Distributors",
                "Diabetes",
                "500mg",
                "TABLET",
                5,
                50,
                500,
                3,
                500,
                50,
            ),
            (
                "Glimepiride",
                "Glimepiride",
                "MediSource Inc",
                "Diabetes",
                "2mg",
                "TABLET",
                8,
                80,
                800,
                6,
                300,
                30,
            ),
            (
                "Antiseptic Cream",
                "Antiseptic",
                "BioGen Pharmaceuticals",
                "First Aid",
                "20g",
                "CREAM",
                80,
                80,
                800,
                55,
                300,
                30,
            ),
        ]

        medicines = []
        purchase_price_map = {}

        for (
            name,
            generic_name,
            manufacturer,
            category_name,
            strength,
            dosage_form,
            pc_price,
            strip_price,
            box_price,
            purchase_price,
            opening_stock,
            minimum_stock,
        ) in medicines_data:

            medicine, _ = Medicine.objects.update_or_create(
                name=name,
                strength=strength,
                dosage_form=dosage_form,
                defaults={
                    "generic_name": generic_name,
                    "manufacturer": manufacturer,
                    "category": cat_map[category_name],
                    "pc_price": Decimal(str(pc_price)),
                    "strip_price": Decimal(str(strip_price)),
                    "box_price": Decimal(str(box_price)),
                    "minimum_stock": minimum_stock,
                    "expiry_date": today + timedelta(days=730),
                    "is_active": True,
                },
            )

            medicines.append(medicine)

            purchase_price_map[medicine.pk] = Decimal(
                str(purchase_price)
            )

            inventory, inventory_created = Inventory.objects.get_or_create(
                medicine=medicine,
                defaults={
                    "current_stock": opening_stock,
                    "minimum_stock": minimum_stock,
                },
            )

            if inventory_created and opening_stock > 0:
                InventoryTransaction.objects.create(
                    inventory=inventory,
                    transaction_type="IN",
                    quantity=opening_stock,
                    previous_stock=0,
                    new_stock=opening_stock,
                    note="Initial seed stock",
                )

        # ---------------------------------------------------------
        # CUSTOMERS
        # ---------------------------------------------------------
        customers_data = [
            ("Abdul Karim", "+8801711111111"),
            ("Fatima Begum", "+8801711111112"),
            ("Hasan Mahmud", "+8801711111113"),
            ("Nasrin Akhter", "+8801711111114"),
            ("Rafiq Hasan", "+8801711111115"),
            ("Shamima Sultana", "+8801711111116"),
            ("Jahangir Alam", "+8801711111117"),
            ("Morsheda Khatun", "+8801711111118"),
            ("Tariq Islam", "+8801711111119"),
            ("Shahinur Rahman", "+8801711111120"),
        ]

        for name, phone in customers_data:
            Customer.objects.get_or_create(
                name=name,
                phone=phone,
            )

        customers = list(Customer.objects.all())

        # ---------------------------------------------------------
        # SALES
        # ---------------------------------------------------------
        for i in range(20):
            invoice_number = f"DEMO-SALE-{1001 + i}"

            if Sale.objects.filter(
                invoice_number=invoice_number
            ).exists():
                continue

            sale_date = today - timedelta(
                days=random.randint(0, 60)
            )

            customer = (
                random.choice(customers)
                if customers and random.random() > 0.3
                else None
            )

            items_count = random.randint(1, 5)

            selected = random.sample(
                medicines,
                min(items_count, len(medicines)),
            )

            total = Decimal("0.00")
            sale_items = []

            for medicine in selected:
                quantity = random.randint(1, 5)
                unit_price = medicine.pc_price
                subtotal = unit_price * quantity

                total += subtotal

                sale_items.append(
                    (
                        medicine,
                        quantity,
                        unit_price,
                        subtotal,
                    )
                )

            discount = Decimal("0.00")

            if total > Decimal("500"):
                discount = (
                    total * Decimal("0.05")
                ).quantize(Decimal("0.01"))

            payable = total - discount

            payment_method = random.choice(
                ["CASH", "CARD", "MOBILE"]
            )

            sale = Sale.objects.create(
                invoice_number=invoice_number,
                customer=customer,
                user=user,
                total_amount=total,
                discount=discount,
                payable_amount=payable,
                payment_method=payment_method,
            )

            # sale_date uses auto_now_add in the model.
            # Update it after creation so demo history can use older dates.
            Sale.objects.filter(pk=sale.pk).update(
                sale_date=sale_date
            )

            for (
                medicine,
                quantity,
                unit_price,
                subtotal,
            ) in sale_items:
                SaleItem.objects.create(
                    sale=sale,
                    medicine=medicine,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                )

        # ---------------------------------------------------------
        # PURCHASES
        # ---------------------------------------------------------
        for i in range(10):
            invoice_number = f"DEMO-PUR-{1001 + i}"

            if Purchase.objects.filter(
                invoice_number=invoice_number
            ).exists():
                continue

            purchase_date = today - timedelta(
                days=random.randint(0, 90)
            )

            supplier = random.choice(suppliers_list)

            items_count = random.randint(2, 6)

            selected = random.sample(
                medicines,
                min(items_count, len(medicines)),
            )

            total = Decimal("0.00")
            purchase_items = []

            for medicine in selected:
                quantity = random.randint(50, 200)

                unit_price = purchase_price_map[
                    medicine.pk
                ]

                subtotal = unit_price * quantity
                total += subtotal

                purchase_items.append(
                    (
                        medicine,
                        quantity,
                        unit_price,
                        subtotal,
                    )
                )

            discount = Decimal("0.00")

            if total > Decimal("10000"):
                discount = (
                    total * Decimal("0.08")
                ).quantize(Decimal("0.01"))

            payable = total - discount

            purchase = Purchase.objects.create(
                invoice_number=invoice_number,
                supplier=supplier,
                user=user,
                total_amount=total,
                discount=discount,
                payable_amount=payable,
                purchase_date=purchase_date,
            )

            for (
                medicine,
                quantity,
                unit_price,
                subtotal,
            ) in purchase_items:
                PurchaseItem.objects.create(
                    purchase=purchase,
                    medicine=medicine,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                    expiry_date=medicine.expiry_date,
                    manufactured_date=(
                        purchase_date - timedelta(days=90)
                    ),
                )

        # ---------------------------------------------------------
        # RESULT
        # ---------------------------------------------------------
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: "
                f"{Category.objects.count()} categories, "
                f"{Supplier.objects.count()} suppliers, "
                f"{Medicine.objects.count()} medicines, "
                f"{Inventory.objects.count()} inventory records, "
                f"{Customer.objects.count()} customers, "
                f"{Sale.objects.count()} sales, "
                f"{Purchase.objects.count()} purchases"
            )
        )