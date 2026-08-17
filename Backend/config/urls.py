"""
URL configuration for the PHARVO project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/inventory/", include("inventory.urls")),
    path("api/customers/", include("customers.urls")),
    path("api/purchases/", include("purchases.urls")),
    path("api/sales/", include("sales.urls")),
    path("api/pos/", include("pos.urls")),
    path("api/crm/", include("crm.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/notifications/", include("notifications.urls")),
]
