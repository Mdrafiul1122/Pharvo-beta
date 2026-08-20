from datetime import datetime

from django.db.models import Q
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.models import (
    Customer,
    CustomerMedicine,
    MedicineReminder,
    MedicineRefillReminder,
)

from customers.serializers import (
    CustomerSerializer,
    CustomerMedicineSerializer,
    MedicineReminderSerializer,
    MedicineRefillReminderSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            Customer.objects
            .prefetch_related(
                "medicines",
                "medicines__reminders",
            )
            .all()
            .order_by("id")
        )

        membership = self.request.query_params.get(
            "membership"
        )

        if membership:
            queryset = queryset.filter(
                membership=membership.upper()
            )

        min_loyalty_points = (
            self.request.query_params.get(
                "min_loyalty_points"
            )
        )

        if min_loyalty_points:
            try:
                points = int(min_loyalty_points)

                queryset = queryset.filter(
                    loyalty_points__gt=points
                )

            except ValueError:
                pass

        return queryset


class CustomerMedicineViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        CustomerMedicine.objects
        .select_related(
            "customer",
            "medicine",
        )
        .prefetch_related(
            "reminders",
        )
        .all()
    )

    serializer_class = (
        CustomerMedicineSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]


class MedicineReminderViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        MedicineReminder.objects
        .select_related(
            "customer_medicine",
            "customer_medicine__customer",
            "customer_medicine__medicine",
        )
        .all()
    )

    serializer_class = (
        MedicineReminderSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]


class MedicineRefillReminderViewSet(
    viewsets.ModelViewSet
):
    serializer_class = (
        MedicineRefillReminderSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            MedicineRefillReminder.objects
            .select_related(
                "customer",
                "medicine",
            )
            .all()
        )

        customer_id = (
            self.request.query_params.get(
                "customer"
            )
        )

        if customer_id:
            queryset = queryset.filter(
                customer_id=customer_id
            )

        is_active = (
            self.request.query_params.get(
                "is_active"
            )
        )

        if is_active == "true":
            queryset = queryset.filter(
                is_active=True
            )

        elif is_active == "false":
            queryset = queryset.filter(
                is_active=False
            )

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="active",
    )
    def active_reminders(self, request):
        reminders = (
            self.get_queryset()
            .filter(is_active=True)
            .order_by(
                "refill_date",
                "refill_time",
            )
        )

        serializer = self.get_serializer(
            reminders,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="upcoming",
    )
    def upcoming_reminders(self, request):
        now = timezone.localtime()

        reminders = (
            self.get_queryset()
            .filter(
                is_active=True,
            )
            .filter(
                Q(
                    refill_date__gt=now.date()
                )
                |
                Q(
                    refill_date=now.date(),
                    refill_time__gte=now.time(),
                )
            )
            .order_by(
                "refill_date",
                "refill_time",
            )
        )

        serializer = self.get_serializer(
            reminders,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="overdue",
    )
    def overdue_reminders(self, request):
        now = timezone.localtime()

        reminders = (
            self.get_queryset()
            .filter(
                is_active=True,
            )
            .filter(
                Q(
                    refill_date__lt=now.date()
                )
                |
                Q(
                    refill_date=now.date(),
                    refill_time__lt=now.time(),
                )
            )
            .order_by(
                "refill_date",
                "refill_time",
            )
        )

        serializer = self.get_serializer(
            reminders,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["patch"],
        url_path="deactivate",
    )
    def deactivate(self, request, pk=None):
        reminder = self.get_object()

        reminder.is_active = False
        reminder.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(
            reminder
        )

        return Response(serializer.data)