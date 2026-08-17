from rest_framework import viewsets

from accounts.permissions import IsStaffOrReadOnly

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        from django.db.models import Q

        queryset = Customer.objects.all()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(phone__icontains=search) | Q(email__icontains=search)
            )
        return queryset
