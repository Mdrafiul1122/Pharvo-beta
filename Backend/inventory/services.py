from datetime import date, timedelta

from django.db.models import F
from rest_framework.exceptions import ValidationError

from .models import Product


def is_expired(expiry_date, on_date=None):
    if expiry_date is None:
        return False
    return expiry_date < (on_date or date.today())


def expiry_status(expiry_date, window_days, on_date=None):
    today = on_date or date.today()
    if expiry_date is None:
        return "valid"
    if expiry_date < today:
        return "expired"
    if expiry_date <= today + timedelta(days=window_days):
        return "near_expiry"
    return "valid"


def _lock_products(items):
    product_ids = sorted({item.product_id for item in items})
    if not product_ids:
        return {}
    products = Product.objects.select_for_update().filter(id__in=product_ids)
    return {product.id: product for product in products}


def _adjust(items, sign):
    _lock_products(items)
    for item in items:
        Product.objects.filter(id=item.product_id).update(
            stock_quantity=F("stock_quantity") + sign * item.quantity
        )


def add_purchase_stock(items):
    _adjust(items, 1)


def remove_purchase_stock(items):
    _adjust(items, -1)


def restore_sale_stock(items):
    _adjust(items, 1)


def deduct_sale_stock(items):
    locked = _lock_products(items)
    for item in items:
        product = locked.get(item.product_id)
        if product is not None and product.stock_quantity < item.quantity:
            raise ValidationError(
                {
                    "items": (
                        f"Insufficient stock for '{product.name}': "
                        f"available {product.stock_quantity}, requested {item.quantity}."
                    )
                }
            )
    for item in items:
        Product.objects.filter(id=item.product_id).update(
            stock_quantity=F("stock_quantity") - item.quantity
        )
