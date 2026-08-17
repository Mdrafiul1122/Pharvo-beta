from rest_framework.routers import DefaultRouter

from .views import CrmCustomerViewSet, ReminderViewSet

router = DefaultRouter()
router.register("customers", CrmCustomerViewSet, basename="crm-customer")
router.register("reminders", ReminderViewSet, basename="reminder")

urlpatterns = router.urls