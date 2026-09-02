from django.utils import timezone

from supplier.models import SupplierOrder

# Allowed status transitions. Keys map to current status values; values are the
# statuses reachable from the current one. Terminal states remain terminal.
_ALLOWED_TRANSITIONS = {
    SupplierOrder.STATUS_REQUESTED: [
        SupplierOrder.STATUS_ORDERED,
        SupplierOrder.STATUS_RECEIVED,
        SupplierOrder.STATUS_CANCELLED,
    ],
    SupplierOrder.STATUS_ORDERED: [
        SupplierOrder.STATUS_RECEIVED,
        SupplierOrder.STATUS_CANCELLED,
    ],
    SupplierOrder.STATUS_RECEIVED: [],
    SupplierOrder.STATUS_CANCELLED: [],
}


def can_transition(status, new_status):
    """Return True if moving from `status` to `new_status` is allowed."""
    if status == new_status:
        return True
    return new_status in _ALLOWED_TRANSITIONS.get(status, [])


def create_supplier_order(supplier, medicine, quantity, supplier_price=None,
                          notes='', user=None):
    """Create a single supplier order. Does NOT touch inventory stock.

    A supplier order is only a request sent to the supplier. Stock increases
    later via the existing Purchases (receiving) flow, not here.
    """
    now = timezone.now()
    order = SupplierOrder.objects.create(
        supplier=supplier,
        medicine=medicine,
        quantity=quantity,
        requested_date=now,
        supplier_price=supplier_price,
        status=SupplierOrder.STATUS_REQUESTED,
        confirmed_by=None,
        confirmed_date=None,
        notes=notes or '',
        created_at=now,
        updated_at=now,
    )
    _log_audit(order, 'created', user=user)
    return order


def update_supplier_order(order, user, status=None, notes=None, supplier_price=None):
    """Apply a safe partial update to an existing order.

    Returns the updated order. Does not change stock. New status must be a
    valid transition, otherwise the status is left unchanged.
    """
    changed = False
    if notes is not None:
        order.notes = notes
        changed = True
    if supplier_price is not None:
        order.supplier_price = supplier_price
        changed = True
    if status is not None and can_transition(order.status, status):
        old_status = order.status
        if status == SupplierOrder.STATUS_RECEIVED and not order.confirmed_date:
            order.confirmed_date = timezone.now()
        if status == SupplierOrder.STATUS_CANCELLED and not order.confirmed_date:
            order.confirmed_date = timezone.now()
        order.status = status
        if status in (SupplierOrder.STATUS_RECEIVED, SupplierOrder.STATUS_CANCELLED):
            order.confirmed_by = user
        order.updated_at = timezone.now()
        changed = True
        if status != old_status:
            _log_audit(order, f'status_{status.lower()}', user=user)
    elif changed:
        order.updated_at = timezone.now()
    if changed:
        order.save()
    return order


def _log_audit(order, event, user=None):
    """Write a single audit row for an order event. Never called on GET."""
    try:
        from audit.services import create_audit_log
    except ImportError:
        return
    details = {
        'module': 'supplier_order',
        'event': event,
        'supplier_order_id': order.pk,
        'supplier_id': order.supplier_id,
        'medicine_id': order.medicine_id,
        'quantity': order.quantity,
        'status': order.status,
    }
    create_audit_log(action=f'supplier_order_{event}', details=details, user=user)
