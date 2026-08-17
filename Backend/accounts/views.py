"""Authentication views: JWT login (role-aware), signup, and current user."""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    PharvTokenObtainPairSerializer,
    SignupSerializer,
    UserSerializer,
)


class PharvTokenObtainPairView(TokenObtainPairView):
    """Login returning access/refresh tokens plus the authenticated user."""

    serializer_class = PharvTokenObtainPairSerializer


class SignupView(APIView):
    """Create a pharmacist or customer account and return tokens for it."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """Return the current authenticated user (server-side role source)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
