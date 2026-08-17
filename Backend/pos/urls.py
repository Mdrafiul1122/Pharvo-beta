from django.urls import path

from .views import PosCheckoutView

urlpatterns = [
    path("checkout/", PosCheckoutView.as_view(), name="pos-checkout"),
]
