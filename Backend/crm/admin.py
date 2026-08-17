from django.contrib import admin

from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "product", "reminder_time", "is_active")
    list_filter = ("is_active", "reminder_time")
    search_fields = ("title", "customer__name", "product__name")