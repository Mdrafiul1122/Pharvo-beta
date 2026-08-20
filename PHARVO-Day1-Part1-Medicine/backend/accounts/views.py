from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserProfile
from accounts.serializers import UserSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            User.objects
            .select_related("profile")
            .all()
            .order_by("id")
        )

        role = self.request.query_params.get(
            "role"
        )

        if role:
            queryset = queryset.filter(
                profile__role=role.lower()
            )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="role-counts",
    )
    def role_counts(self, request):
        rows = (
            UserProfile.objects
            .values("role")
            .annotate(
                total=Count("id")
            )
        )

        result = {
            "admin": 0,
            "pharmacist": 0,
            "customer": 0,
        }

        for row in rows:
            result[row["role"]] = row["total"]

        return Response(result)