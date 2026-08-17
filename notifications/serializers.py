from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "severity",
            "is_read",
            "product",
            "product_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "type",
            "title",
            "message",
            "severity",
            "is_read",
            "product",
            "created_at",
        ]