from django.db import transaction
from rest_framework import permissions, viewsets

from inventory.services import deduct_sale_stock, restore_sale_stock

from .models import Sale
from .serializers import SaleSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return user.is_staff


class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        with transaction.atomic():
            sale = serializer.save()
            deduct_sale_stock(sale.items.all())

    def perform_update(self, serializer):
        with transaction.atomic():
            old_items = list(serializer.instance.items.all())
            restore_sale_stock(old_items)
            sale = serializer.save()
            deduct_sale_stock(sale.items.all())

    def perform_destroy(self, instance):
        with transaction.atomic():
            items = list(instance.items.all())
            restore_sale_stock(items)
            instance.delete()

    def get_queryset(self):
        from django.db.models import Q

        queryset = Sale.objects.select_related("customer", "user").prefetch_related(
            "items__product"
        )
        search = self.request.query_params.get("search")
        customer = self.request.query_params.get("customer")
        user = self.request.query_params.get("user")
        payment_method = self.request.query_params.get("payment_method")
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search)
                | Q(customer__name__icontains=search)
                | Q(user__username__icontains=search)
            )
        if customer:
            queryset = queryset.filter(customer_id=customer)
        if user:
            queryset = queryset.filter(user_id=user)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        return queryset
