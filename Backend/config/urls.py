"""
URL configuration for the PHARVO project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
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
