from django.urls import path

from django.urls import path

from dashboard.views import (
    OwnerDashboardView,
    AdvancedReportsView,
)


urlpatterns = [
    path(
        "overview/",
        OwnerDashboardView.as_view(),
        name="owner-dashboard",
    ),
    path(
    "advanced-reports/",
    AdvancedReportsView.as_view(),
    ),
]