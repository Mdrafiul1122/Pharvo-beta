from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from supplier.models import SupplierOrder
from supplier.permissions import IsSupplierOrderStaff
from supplier.serializers import (
    SupplierOrderCreateSerializer,
    SupplierOrderSerializer,
    SupplierOrderUpdateSerializer,
)
from supplier.services import create_supplier_order, update_supplier_order


class SupplierOrderListView(generics.ListAPIView):
    serializer_class = SupplierOrderSerializer
    permission_classes = [IsSupplierOrderStaff]

    def get_queryset(self):
        qs = (
            SupplierOrder.objects.select_related('supplier', 'medicine', 'confirmed_by')
            .order_by('-created_at', '-id')
        )

        supplier = self.request.query_params.get('supplier')
        if supplier:
            qs = qs.filter(supplier_id=supplier)

        status_val = self.request.query_params.get('status')
        if status_val:
            qs = qs.filter(status=status_val.upper())

        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(requested_date__date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(requested_date__date__lte=end_date)

        return qs


class SupplierOrderDetailView(generics.RetrieveAPIView):
    serializer_class = SupplierOrderSerializer
    permission_classes = [IsSupplierOrderStaff]
    queryset = SupplierOrder.objects.select_related('supplier', 'medicine', 'confirmed_by')


class SupplierOrderCreateView(APIView):
    permission_classes = [IsSupplierOrderStaff]

    def post(self, request):
        serializer = SupplierOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = create_supplier_order(
            supplier=data['supplier'],
            medicine=data['medicine'],
            quantity=data['quantity'],
            supplier_price=data.get('supplier_price'),
            notes=data.get('notes', ''),
            user=request.user,
        )
        output = SupplierOrderSerializer(
            SupplierOrder.objects.select_related('supplier', 'medicine', 'confirmed_by')
            .get(pk=order.pk)
        ).data
        return Response(output, status=status.HTTP_201_CREATED)


class SupplierOrderUpdateView(APIView):
    permission_classes = [IsSupplierOrderStaff]

    def patch(self, request, pk):
        try:
            order = SupplierOrder.objects.get(pk=pk)
        except SupplierOrder.DoesNotExist:
            return Response(
                {'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierOrderUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order = update_supplier_order(
            order,
            user=request.user,
            status=data.get('status'),
            notes=data.get('notes'),
            supplier_price=data.get('supplier_price'),
        )
        output = SupplierOrderSerializer(
            SupplierOrder.objects.select_related('supplier', 'medicine', 'confirmed_by')
            .get(pk=order.pk)
        ).data
        return Response(output)
