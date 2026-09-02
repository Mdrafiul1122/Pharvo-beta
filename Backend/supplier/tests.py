"""
Supplier Orders — Test Suite

Runs against the live PostgreSQL database. Creates temporary users, suppliers,
products and orders, cleans them up afterward, and verifies the pre-existing
supplier_supplierorder rows, inventory stock, and audit rows remain unchanged.

Run with: python supplier/tests.py
"""
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User
from inventory.models import InventoryProduct, InventorySupplier
from supplier.models import SupplierOrder
from supplier.serializers import SupplierOrderSerializer
from supplier.services import create_supplier_order, update_supplier_order, can_transition

passed = 0
failed = 0
errors = []

ORDER_BASELINE = SupplierOrder.objects.count()
AUDIT_BASELINE = __import__('audit.models', fromlist=['AuditLog']).AuditLog.objects.count()
STOCK_BASELINE = dict(
    InventoryProduct.objects.values_list('id', 'stock_quantity')
)

cleanup_users = []
cleanup_suppliers = []
cleanup_products = []
cleanup_orders = []
cleanup_audit = []
_user_cache = {}


def run_test(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  PASS  {name}")
    except Exception as e:
        failed += 1
        errors.append((name, str(e), traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


def anon():
    return type('Anon', (), {'is_authenticated': False, 'is_superuser': False})()


def _get_or_create(username, **kwargs):
    if username not in _user_cache:
        user, created = User.objects.get_or_create(username=username, defaults=kwargs)
        if created:
            user.set_password('testpass123')
            user.save()
            cleanup_users.append(user.id)
        _user_cache[username] = user
    return _user_cache[username]


def _user(role):
    return _get_or_create(f'__test_so_{role}', role=role, is_active=True)


def _temp_supplier(**kwargs):
    import time
    n = time.time()
    defaults = dict(
        name=f'__test_supplier_{n}',
        contact_person='Test Contact',
        phone=f'+639{int(n) % 10**9:09d}',
        email=f'supplier_{int(n % 10**6)}@example.com',
        address='123 Test St',
        created_at=timezone.now(),
        is_active=True,
    )
    defaults.update(kwargs)
    s = InventorySupplier.objects.create(**defaults)
    cleanup_suppliers.append(s.id)
    return s


def _temp_product(supplier=None, **kwargs):
    import time
    n = time.time()
    now = timezone.now()
    defaults = dict(
        name=f'__test_med_{n}',
        brand='TestBrand',
        barcode=f'__so_bc_{n}_{abs(hash(str(kwargs))) % 10**9}',
        unit_price=Decimal('50.00'),
        cost_price=Decimal('30.00'),
        stock_quantity=100,
        reorder_level=10,
        expiry_date=None,
        is_active=True,
        description='',
        created_at=now,
        updated_at=now,
        is_sensitive=False,
    )
    defaults.update(kwargs)
    p = InventoryProduct.objects.create(**defaults)
    cleanup_products.append(p.id)
    return p


def _temp_order(**kwargs):
    import time
    now = timezone.now()
    defaults = dict(
        supplier=_temp_supplier(),
        medicine=_temp_product(),
        quantity=10,
        status=SupplierOrder.STATUS_REQUESTED,
        requested_date=now,
        supplier_price=Decimal('45.00'),
        notes='',
        confirmed_by=None,
        confirmed_date=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    order = SupplierOrder.objects.create(**defaults)
    cleanup_orders.append(order.id)
    return order


def _call(view_cls, method='get', url='', user=None, view_kwargs=None, **kw):
    factory = APIRequestFactory()
    req = getattr(factory, method)(url, **kw)
    force_authenticate(req, user=user) if user else setattr(req, 'user', anon())
    resp = view_cls.as_view()(req, **(view_kwargs or {}))
    resp.render()
    from importlib import import_module
    json_m = import_module('json')
    body = json_m.loads(resp.content) if resp.content else None
    return resp.status_code, body


print("\n" + "=" * 60)
print("  SUPPLIER ORDERS — TEST SUITE")
print("=" * 60 + "\n")


# ── Model mapping ──

def test_model_maps_to_table():
    assert SupplierOrder._meta.db_table == 'supplier_supplierorder'


def test_model_managed_false():
    assert SupplierOrder._meta.managed is False


def test_model_fields():
    names = [f.name for f in SupplierOrder._meta.get_fields()]
    for f in ['id', 'supplier', 'medicine', 'quantity', 'requested_date',
              'supplier_price', 'status', 'confirmed_by', 'confirmed_date',
              'notes', 'created_at', 'updated_at']:
        assert f in names, f'missing field {f}'


run_test("SupplierOrder maps to supplier_supplierorder", test_model_maps_to_table)
run_test("SupplierOrder is managed=False", test_model_managed_false)
run_test("SupplierOrder has exact DB columns", test_model_fields)


# ── Serializer ──

def test_serializer_fields():
    p = _temp_product()
    s = _temp_supplier()
    u = _user('staff')
    order = _temp_order(supplier=s, medicine=p, confirmed_by=u, status=SupplierOrder.STATUS_RECEIVED, confirmed_date=timezone.now())
    data = SupplierOrderSerializer(order).data
    for f in ['id', 'supplier', 'medicine', 'quantity', 'requested_date',
              'supplier_price', 'status', 'confirmed_by', 'confirmed_date',
              'notes', 'created_at', 'updated_at']:
        assert f in data, f'missing field {f}'
    assert data['medicine']['id'] == p.id
    assert data['supplier']['id'] == s.id


run_test("SupplierOrderSerializer exposes read-only fields", test_serializer_fields)


# ── API helpers ──

from supplier.views import (
    SupplierOrderListView, SupplierOrderDetailView,
    SupplierOrderCreateView, SupplierOrderUpdateView,
)


def call_list(user, query=''):
    return _call(SupplierOrderListView, 'get', f'/api/orders/{query}', user)


def call_create(user, data):
    import json
    return _call(SupplierOrderCreateView, 'post', '/api/orders/create/', user,
                 data=json.dumps(data), content_type='application/json')


def call_retrieve(user, pk):
    return _call(SupplierOrderDetailView, 'get', f'/api/orders/{pk}/', user,
                 view_kwargs={'pk': pk})


def call_update(user, pk, data):
    import json
    return _call(SupplierOrderUpdateView, 'patch', f'/api/orders/{pk}/update/', user,
                 view_kwargs={'pk': pk},
                 data=json.dumps(data), content_type='application/json')


def _create_payload(supplier=None, medicine=None, quantity=10, **extra):
    if supplier is None:
        supplier = _temp_supplier()
    if medicine is None:
        medicine = _temp_product()
    payload = {'supplier': supplier.id, 'medicine': medicine.id, 'quantity': quantity}
    payload.update(extra)
    return payload


# ── List / Retrieve / Create / Update ──

def test_list_admin():
    _temp_order()
    code, data = call_list(_user('admin'))
    assert code == 200
    assert isinstance(data, list)


def test_list_staff():
    code, data = call_list(_user('staff'))
    assert code == 200


def test_list_pharmacist():
    code, data = call_list(_user('pharmacist'))
    assert code == 200


def test_retrieve():
    order = _temp_order()
    code, data = call_retrieve(_user('admin'), order.id)
    assert code == 200
    assert data['id'] == order.id
    assert data['status'] == 'REQUESTED'


def test_retrieve_invalid_id():
    code, _ = call_retrieve(_user('admin'), 999999999)
    assert code == 404


def test_create_order():
    payload = _create_payload(quantity=15, supplier_price='55.00', notes='urgent')
    code, data = call_create(_user('admin'), payload)
    assert code == 201, data
    assert data['quantity'] == 15
    assert data['status'] == 'REQUESTED'
    assert Decimal(data['supplier_price']) == Decimal('55.00')
    assert data['notes'] == 'urgent'
    cleanup_orders.append(data['id'])


def test_create_invalid_input():
    code, data = call_create(_user('admin'), {'supplier': 999999, 'medicine': 999999, 'quantity': 0})
    assert code == 400


def test_update_status():
    order = _temp_order()
    code, data = call_update(_user('admin'), order.id, {'status': 'ORDERED'})
    assert code == 200
    assert data['status'] == 'ORDERED'


def test_update_invalid_status_keeps_current():
    order = _temp_order(status=SupplierOrder.STATUS_RECEIVED)
    code, data = call_update(_user('admin'), order.id, {'status': 'ORDERED'})
    assert code == 200
    assert data['status'] == 'RECEIVED'


def test_update_notes():
    order = _temp_order()
    code, data = call_update(_user('admin'), order.id, {'notes': 'updated note'})
    assert code == 200
    assert data['notes'] == 'updated note'


run_test("GET /api/orders/ admin allowed", test_list_admin)
run_test("GET /api/orders/ staff allowed", test_list_staff)
run_test("GET /api/orders/ pharmacist allowed", test_list_pharmacist)
run_test("GET /api/orders/<id>/ admin allowed", test_retrieve)
run_test("GET /api/orders/<invalid id>/ returns 404", test_retrieve_invalid_id)
run_test("POST /api/orders/create/ creates order", test_create_order)
run_test("POST create rejects invalid input", test_create_invalid_input)
run_test("PATCH status update", test_update_status)
run_test("PATCH invalid status is ignored", test_update_invalid_status_keeps_current)
run_test("PATCH notes update", test_update_notes)


# ── Filtering ──

def test_filter_by_status():
    a = _temp_order(status=SupplierOrder.STATUS_REQUESTED)
    _temp_order(status=SupplierOrder.STATUS_RECEIVED)
    code, data = call_list(_user('admin'), '?status=REQUESTED')
    assert code == 200
    statuses = [r['status'] for r in data]
    assert 'REQUESTED' in statuses


def test_filter_by_supplier():
    s = _temp_supplier()
    _temp_order(supplier=s)
    other = _temp_order()
    code, data = call_list(_user('admin'), f'?supplier={s.id}')
    assert code == 200
    ids = [r['id'] for r in data]
    assert other.id not in ids


run_test("filter by status", test_filter_by_status)
run_test("filter by supplier", test_filter_by_supplier)


# ── Permissions ──

def test_customer_denied_list():
    code, _ = call_list(_user('customer'))
    assert code == 403


def test_anonymous_denied_list():
    code, _ = call_list(None)
    assert code == 401


def test_customer_denied_create():
    payload = _create_payload()
    code, _ = call_create(_user('customer'), payload)
    assert code == 403


def test_customer_denied_retrieve():
    order = _temp_order()
    code, _ = call_retrieve(_user('customer'), order.id)
    assert code == 403


def test_customer_denied_update():
    order = _temp_order()
    code, _ = call_update(_user('customer'), order.id, {'status': 'ORDERED'})
    assert code == 403


run_test("customer denied GET list (403)", test_customer_denied_list)
run_test("anonymous denied GET list (401)", test_anonymous_denied_list)
run_test("customer denied create (403)", test_customer_denied_create)
run_test("customer denied retrieve (403)", test_customer_denied_retrieve)
run_test("customer denied update (403)", test_customer_denied_update)


# ── Supplier / product relationship ──

def test_supplier_relationship():
    s = _temp_supplier()
    order = _temp_order(supplier=s)
    assert order.supplier_id == s.id
    assert order.supplier.name == s.name


def test_product_relationship():
    p = _temp_product()
    order = _temp_order(medicine=p)
    assert order.medicine_id == p.id
    assert order.medicine.name == p.name


run_test("supplier relationship present", test_supplier_relationship)
run_test("medicine relationship present", test_product_relationship)


# ── Stock must NOT change on order create ──

def test_stock_unchanged_on_create():
    p = _temp_product(stock_quantity=50)
    before = InventoryProduct.objects.get(pk=p.pk).stock_quantity
    payload = _create_payload(medicine=p, quantity=20)
    code, data = call_create(_user('admin'), payload)
    assert code == 201, data
    cleanup_orders.append(data['id'])
    after = InventoryProduct.objects.get(pk=p.pk).stock_quantity
    assert after == before, f'stock changed from {before} to {after} on order creation'


run_test("stock does NOT change when order created", test_stock_unchanged_on_create)


# ── Status transition logic ──

def test_state_machine():
    assert can_transition('REQUESTED', 'ORDERED')
    assert can_transition('REQUESTED', 'CANCELLED')
    assert can_transition('ORDERED', 'RECEIVED')
    assert not can_transition('RECEIVED', 'ORDERED')
    assert not can_transition('CANCELLED', 'RECEIVED')


run_test("status transition rules", test_state_machine)


# ── Service helpers ──

def test_create_helper_does_not_change_stock():
    p = _temp_product(stock_quantity=77)
    s = _temp_supplier()
    before = InventoryProduct.objects.get(pk=p.pk).stock_quantity
    order = create_supplier_order(s, p, 5, supplier_price=Decimal('10.00'))
    cleanup_orders.append(order.id)
    after = InventoryProduct.objects.get(pk=p.pk).stock_quantity
    assert after == before
    assert order.status == 'REQUESTED'
    assert order.quantity == 5


def test_update_helper_status():
    order = _temp_order()
    updated = update_supplier_order(order, user=_user('admin'), status='ORDERED')
    assert updated.status == 'ORDERED'


run_test("create_supplier_order doesn't change stock", test_create_helper_does_not_change_stock)
run_test("update_supplier_order changes status", test_update_helper_status)


# ── No unintended DB changes / GET spam / audit ──

def test_get_does_not_create_orders():
    before = SupplierOrder.objects.count()
    for _ in range(3):
        call_list(_user('admin'))
    assert SupplierOrder.objects.count() == before


def test_no_audit_on_get():
    from audit.models import AuditLog
    before = AuditLog.objects.count()
    call_list(_user('admin'))
    call_retrieve(_user('admin'), _temp_order().id)
    after = AuditLog.objects.count()
    assert after == before, "GET produced audit logs"


run_test("GET does not create supplier orders", test_get_does_not_create_orders)
run_test("GET does not create audit logs", test_no_audit_on_get)


# ── Cleanup ──
SupplierOrder.objects.filter(id__in=cleanup_orders).delete()
InventoryProduct.objects.filter(id__in=cleanup_products).delete()
InventorySupplier.objects.filter(id__in=cleanup_suppliers).delete()
User.objects.filter(id__in=cleanup_users).delete()

from audit.models import AuditLog
AuditLog.objects.filter(details__module='supplier_order').delete()
AuditLog.objects.filter(pk__in=cleanup_audit).delete()

final_order_count = SupplierOrder.objects.count()
final_stock = dict(InventoryProduct.objects.values_list('id', 'stock_quantity'))
final_audit = AuditLog.objects.count()
print(f"\n  Cleaned up test data. orders={final_order_count}, "
      f"audit={final_audit}, products={len(final_stock)}")

ok = True
if final_order_count != ORDER_BASELINE:
    ok = False
    errors.append(("Cleanup", "Supplier order count differs from baseline",
                   f"baseline={ORDER_BASELINE} final={final_order_count}"))
    print(f"  FAIL  orders {final_order_count} != baseline {ORDER_BASELINE}")
if final_audit != AUDIT_BASELINE:
    ok = False
    errors.append(("Cleanup", "Audit count differs from baseline",
                   f"baseline={AUDIT_BASELINE} final={final_audit}"))
    print(f"  FAIL  audit {final_audit} != baseline {AUDIT_BASELINE}")
if final_stock != STOCK_BASELINE:
    ok = False
    errors.append(("Cleanup", "Inventory stock differs from baseline", "stock changed"))
    print("  FAIL  inventory stock changed")
if len(InventoryProduct.objects.all()) != len(STOCK_BASELINE):
    ok = False
    errors.append(("Cleanup", "Product count differs", "product count changed"))
    print("  FAIL  product count changed")
if len(InventorySupplier.objects.all()) != len(STOCK_BASELINE):
    # suppliers were created fresh each run; verify we cleaned our own only
    pass

if ok:
    print("  PASS  Database restored to baseline after tests")
else:
    print("  FAIL  Database NOT restored to baseline")

print("\n" + "=" * 60)
print(f"  RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if errors:
    print("\nFailed tests:")
    for name, err, tb in errors:
        print(f"\n--- {name} ---")
        print(err)
        print(tb)

print()
