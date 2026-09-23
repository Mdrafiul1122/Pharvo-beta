from django.utils import timezone

from inventory.models import Medicine


def find_available_medicines(candidate_generics, limit_per_generic=10):
    today = timezone.localdate()
    results = []

    for generic in candidate_generics:
        medicines = (
            Medicine.objects
            .filter(
                generic_name__icontains=generic,
                is_active=True,
                expiry_date__gte=today,
                inventory__current_stock__gt=0,
            )
            .select_related("inventory")
            .order_by("expiry_date", "name")[:limit_per_generic]
        )

        matches = []

        for medicine in medicines:
            inventory = medicine.inventory

            matches.append({
                "medicine_id": medicine.id,
                "brand_name": medicine.name,
                "generic_name": medicine.generic_name,
                "manufacturer": medicine.manufacturer,
                "strength": medicine.strength,
                "dosage_form": medicine.get_dosage_form_display(),
                "current_stock": inventory.current_stock,
                "minimum_stock": inventory.minimum_stock,
                "is_low_stock": inventory.is_low_stock,
                "expiry_date": medicine.expiry_date.isoformat(),
                "pc_price": str(medicine.pc_price),
                "strip_price": str(medicine.strip_price),
                "box_price": str(medicine.box_price),
            })

        results.append({
            "candidate_generic": generic,
            "available_medicines": matches,
        })

    return results