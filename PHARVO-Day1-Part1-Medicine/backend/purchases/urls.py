from django.urls import path, include
from rest_framework.routers import DefaultRouter

from purchases.views import PurchaseViewSet, PurchaseItemViewSet

router = DefaultRouter()
router.register(r"purchases", PurchaseViewSet)
router.register(r"purchase-items", PurchaseItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
