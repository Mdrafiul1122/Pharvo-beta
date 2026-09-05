from django.urls import path

from supplier.views import (
    SupplierOrderCreateView,
    SupplierOrderDetailView,
    SupplierOrderListView,
    SupplierOrderUpdateView,
)

urlpatterns = [
    path('orders/', SupplierOrderListView.as_view(), name='supplier-order-list'),
    path('orders/create/', SupplierOrderCreateView.as_view(), name='supplier-order-create'),
    path('orders/<int:pk>/', SupplierOrderDetailView.as_view(), name='supplier-order-detail'),
    path('orders/<int:pk>/update/', SupplierOrderUpdateView.as_view(), name='supplier-order-update'),
]
