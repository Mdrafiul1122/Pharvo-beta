from datetime import date

from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "address",
            "date_of_birth",
            "notes",
            "membership_tier",
            "member_since",
            "is_member",
            "loyalty_points",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_is_member(self, obj):
        return obj.is_member

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Customer name cannot be blank.")
        return name

    def validate_phone(self, value):
        phone = value.strip()
        if not phone:
            raise serializers.ValidationError("Phone number cannot be blank.")
        if len(phone) > 20:
            raise serializers.ValidationError("Phone number cannot exceed 20 characters.")
        return phone

    def validate_email(self, value):
        email = value.strip()
        if not email:
            raise serializers.ValidationError("Email cannot be blank.")
        return email

    def validate_address(self, value):
        address = value.strip()
        if not address:
            raise serializers.ValidationError("Address cannot be blank.")
        return address

    def validate_loyalty_points(self, value):
        if value < 0:
            raise serializers.ValidationError("Loyalty points cannot be negative.")
        return value

    def validate_membership_tier(self, value):
        valid_tiers = {tier for tier, _ in Customer.MembershipTier.choices}
        if value not in valid_tiers:
            raise serializers.ValidationError(
                f"Membership tier must be one of: {', '.join(sorted(valid_tiers)) or 'non-member'}."
            )
        return value

    def validate_date_of_birth(self, value):
        if value is not None and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
