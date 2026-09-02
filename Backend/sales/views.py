import secrets
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import connection, models, transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import InventoryProduct
from sales.models import Sale, SaleItem, SalePayment
from sales.permissions import IsPosStaff
from sales.serializers import CheckoutSerializer, SaleSerializer

CENT = Decimal('0.01')
POS_ADVISORY_LOCK = 466001


def _money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def _next_pk(cursor, db_table):
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM %s" % db_table)
    return cursor.fetchone()[0]


def _unit_factor(product, unit):
    if unit == 'pc':
        return 1
    if unit == 'strip':
        return product.pcs_per_strip
    if unit == 'box':
        return product.pcs_per_box
    return None


def _generate_invoice_number(when):
    prefix = when.strftime('INV-%Y%m%d%H%M%S-')
    while True:
        candidate = prefix + secrets.token_hex(2).upper()
        if not Sale.objects.filter(invoice_number=candidate).exists():
            return candidate


def _create_sale(user, data):
    items = data['items']
    payments = data['payments']
    discount = _money(data.get('discount', 0))
    customer = data.get('customer')

    with transaction.atomic():
        cursor = connection.cursor()
        cursor.execute('SELECT pg_advisory_xact_lock(%s)', [POS_ADVISORY_LOCK])

        sale_id = _next_pk(cursor, 'sales_sale')
        item_id = _next_pk(cursor, 'sales_saleitem')
        payment_id = _next_pk(cursor, 'sales_salepayment')

        now = timezone.now()
        sale_date = timezone.localdate()

        locked = {}
        prepared_items = []
        grand_total = Decimal('0')

        for item in items:
            product = locked.get(item['product'].pk)
            if product is None:
                product = InventoryProduct.objects.select_for_update().get(pk=item['product'].pk)
                locked[product.pk] = product

            unit = item['unit']
            qty = item['quantity']
            price = _money(item['unit_price'])
            factor = _unit_factor(product, unit)
            if factor is None:
                raise ValidationError(
                    "Unit '%s' is not supported for product '%s'." % (unit, product.name)
                )

            quantity_pcs = qty * factor
            if product.stock_quantity < quantity_pcs:
                raise ValidationError(
                    "Insufficient stock for product '%s' (available: %s)."
                    % (product.name, product.stock_quantity)
                )

            subtotal = _money(qty * price)
            grand_total += subtotal
            prepared_items.append((product, item, unit, qty, price, quantity_pcs, subtotal))

        total_amount = _money(grand_total)
        payable_amount = _money(total_amount - discount)
        if payable_amount < 0:
            raise ValidationError('Discount exceeds total amount.')

        payment_total = _money(sum(p['amount'] for p in payments))
        if payment_total != payable_amount:
            raise ValidationError(
                'Payment total %s does not match payable amount %s.'
                % (payment_total, payable_amount)
            )

        invoice_number = _generate_invoice_number(now)
        payment_method = payments[0]['method']

        sale = Sale.objects.create(
            id=sale_id,
            invoice_number=invoice_number,
            total_amount=total_amount,
            discount=discount,
            payable_amount=payable_amount,
            payment_method=payment_method,
            sale_date=sale_date,
            created_at=now,
            customer=customer,
            user=user,
        )

        for product, item, unit, qty, price, quantity_pcs, subtotal in prepared_items:
            SaleItem.objects.create(
                id=item_id,
                sale=sale,
                product=product,
                quantity=qty,
                unit=unit,
                quantity_pcs=quantity_pcs,
                unit_price=price,
                subtotal=subtotal,
            )
            item_id += 1

        for p in payments:
            SalePayment.objects.create(
                id=payment_id,
                sale=sale,
                method=p['method'],
                amount=_money(p['amount']),
                created_at=now,
            )
            payment_id += 1

        deductions = {}
        for product, item, unit, qty, price, quantity_pcs, subtotal in prepared_items:
            deductions[product.pk] = deductions.get(product.pk, 0) + quantity_pcs

        for product_pk, pieces in deductions.items():
            InventoryProduct.objects.filter(pk=product_pk).update(
                stock_quantity=models.F('stock_quantity') - pieces,
                updated_at=now,
            )

        return (
            Sale.objects.select_related('customer', 'user')
            .prefetch_related('items__product', 'payments')
            .get(pk=sale.pk)
        )


class CheckoutView(APIView):
    permission_classes = [IsPosStaff]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            sale = _create_sale(request.user, data)
        except ValidationError as exc:
            return Response({'detail': list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)


class SaleListView(generics.ListAPIView):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Sale.objects.select_related('customer', 'user')
            .prefetch_related('items__product', 'payments')
            .order_by('-created_at')
        )