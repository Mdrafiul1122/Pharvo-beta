from django.utils import timezone
from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    member_since = serializers.DateField(required=False, allow_null=True)
    loyalty_points = serializers.IntegerField(required=False, default=0)
    membership_tier = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default='regular',
    )
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'name',
            'phone',
            'email',
            'address',
            'loyalty_points',
            'created_at',
            'date_of_birth',
            'member_since',
            'membership_tier',
            'notes',
            'is_member',
        ]
        read_only_fields = ['id', 'created_at', 'is_member']

    def validate_membership_tier(self, value):
        if not value or not str(value).strip():
            return 'regular'
        return str(value).strip().lower()

    def get_is_member(self, obj):
        tier = (getattr(obj, 'membership_tier', '') or '').strip().lower()
        return tier in ('bronze', 'silver', 'gold')

    def create(self, validated_data):
        validated_data.setdefault('created_at', timezone.now())
        validated_data.setdefault('loyalty_points', 0)
        validated_data.setdefault('membership_tier', 'regular')
        validated_data.setdefault('notes', '')
        return super().create(validated_data)
