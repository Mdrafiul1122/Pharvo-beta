from django.urls import path, include
from rest_framework.routers import DefaultRouter

from customers.views import (
    CustomerViewSet,
    CustomerMedicineViewSet,
    MedicineReminderViewSet,
    MedicineRefillReminderViewSet,
)


router = DefaultRouter()

router.register(
    r"customers",
    CustomerViewSet,
    basename="customers",
)

router.register(
    r"customer-medicines",
    CustomerMedicineViewSet,
)

router.register(
    r"medicine-reminders",
    MedicineReminderViewSet,
)

router.register(
    r"refill-reminders",
    MedicineRefillReminderViewSet,
    basename="refill-reminders",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]