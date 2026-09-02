from django.urls import path

from sales.views import CheckoutView, SaleListView

urlpatterns = [
    path('pos/checkout/', CheckoutView.as_view(), name='pos-checkout'),
    path('sales/', SaleListView.as_view(), name='sales-list'),
]