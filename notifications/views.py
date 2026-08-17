from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from .services import refresh_alerts


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.select_related("product")
        is_read = self.request.query_params.get("is_read")
        severity = self.request.query_params.get("severity")
        notification_type = self.request.query_params.get("type")
        if is_read is not None:
            queryset = queryset.filter(
                is_read=is_read.lower() in ("1", "true", "yes")
            )
        if severity:
            queryset = queryset.filter(severity=severity)
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        return queryset

    def list(self, request, *args, **kwargs):
        refresh_alerts()
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="read")
    def read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        marked = Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({"marked_read": marked})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        refresh_alerts()
        count = Notification.objects.filter(is_read=False).count()
        return Response({"unread_count": count})