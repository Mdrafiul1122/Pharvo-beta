from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventory.views import (
    CategoryViewSet,
    SupplierViewSet,
    MedicineGroupViewSet,
    MedicineViewSet,
    InventoryViewSet,
    InventoryTransactionViewSet,
    NotificationViewSet,
)


router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
)

router.register(
    r"suppliers",
    SupplierViewSet,
)

router.register(
    r"medicine-groups",
    MedicineGroupViewSet,
)

router.register(
    r"medicines",
    MedicineViewSet,
    basename="medicines",
)

router.register(
    r"inventory",
    InventoryViewSet,
    basename="inventory",
)

router.register(
    r"transactions",
    InventoryTransactionViewSet,
)

router.register(
    r"notifications",
    NotificationViewSet,
    basename="notifications",
)

urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]