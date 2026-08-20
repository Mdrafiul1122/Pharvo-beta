from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sales.views import (
    SaleViewSet,
    SaleItemViewSet,
    SalePaymentViewSet,
)


router = DefaultRouter()

router.register(
    r"sales",
    SaleViewSet,
    basename="sales",
)

router.register(
    r"sale-items",
    SaleItemViewSet,
)

router.register(
    r"sale-payments",
    SalePaymentViewSet,
    basename="sale-payments",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]