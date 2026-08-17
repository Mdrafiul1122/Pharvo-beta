from datetime import date, timedelta

from inventory.models import Product
from inventory.services import expiry_status
from inventory.views import NEAR_EXPIRY_DAYS

from .models import Notification

SEVERITY_BY_TYPE = {
    Notification.Type.LOW_STOCK: Notification.Severity.WARNING,
    Notification.Type.OUT_OF_STOCK: Notification.Severity.CRITICAL,
    Notification.Type.EXPIRED: Notification.Severity.CRITICAL,
    Notification.Type.NEAR_EXPIRY: Notification.Severity.WARNING,
}


def build_dedup_key(alert_type, product_id, status):
    return f"{alert_type}:{product_id}:{status}"


def _alert_payload(alert_type, product):
    name = product.name
    if alert_type == Notification.Type.LOW_STOCK:
        title = f"Low stock: {name}"
        message = (
            f"Only {product.stock_quantity} unit(s) left. "
            f"Reorder level is {product.reorder_level}."
        )
        status = str(product.stock_quantity)
    elif alert_type == Notification.Type.OUT_OF_STOCK:
        title = f"Out of stock: {name}"
        message = "This product has no stock available."
        status = str(product.stock_quantity)
    elif alert_type == Notification.Type.EXPIRED:
        title = f"Expired: {name}"
        message = f"Expired on {product.expiry_date}."
        status = product.expiry_date.isoformat()
    else:  # NEAR_EXPIRY
        title = f"Near expiry: {name}"
        message = (
            f"Expires on {product.expiry_date} within the "
            f"{NEAR_EXPIRY_DAYS}-day window."
        )
        status = product.expiry_date.isoformat()
    return title, message, status


def refresh_alerts():
    """Regenerate current alerts from live product state.

    Deduplicated by a stable key (type + product + relevant date/status), so
    repeated calls never create duplicates. Alerts whose condition no longer
    holds are automatically marked as read.
    """
    today = date.today()
    window_end = today + timedelta(days=NEAR_EXPIRY_DAYS)
    current_keys = set()
    products = Product.objects.filter(is_active=True).only(
        "id", "name", "stock_quantity", "reorder_level", "expiry_date"
    )
    for product in products:
        expiry_state = expiry_status(product.expiry_date, NEAR_EXPIRY_DAYS, today)
        alerts = []
        if expiry_state == "expired":
            alerts.append(Notification.Type.EXPIRED)
        elif expiry_state == "near_expiry":
            alerts.append(Notification.Type.NEAR_EXPIRY)
        if product.stock_quantity <= 0:
            alerts.append(Notification.Type.OUT_OF_STOCK)
        elif product.stock_quantity <= product.reorder_level:
            alerts.append(Notification.Type.LOW_STOCK)
        for alert_type in alerts:
            title, message, status = _alert_payload(alert_type, product)
            key = build_dedup_key(alert_type, product.id, status)
            current_keys.add(key)
            Notification.objects.get_or_create(
                dedup_key=key,
                defaults={
                    "type": alert_type,
                    "title": title,
                    "message": message,
                    "severity": SEVERITY_BY_TYPE[alert_type],
                    "product_id": product.id,
                },
            )
    Notification.objects.filter(is_read=False).exclude(
        dedup_key__in=current_keys
    ).update(is_read=True)
    return len(current_keys)