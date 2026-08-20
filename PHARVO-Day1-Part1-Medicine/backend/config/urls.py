from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/auth/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    path(
        "api/auth/token/verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),

    path("api/inventory/", include("inventory.urls")),
    path("api/customers/", include("customers.urls")),
    path("api/sales/", include("sales.urls")),
    path("api/purchases/", include("purchases.urls")),
    path("api/interactions/", include("interactions.urls")),

    path(
        "api/dashboard/",
        include("dashboard.urls"),
    ),
    
    path(
    "api/accounts/",
    include("accounts.urls"),
),
]
