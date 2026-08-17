from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, PharvTokenObtainPairView, SignupView

urlpatterns = [
    path("login/", PharvTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("me/", MeView.as_view(), name="me"),
]
