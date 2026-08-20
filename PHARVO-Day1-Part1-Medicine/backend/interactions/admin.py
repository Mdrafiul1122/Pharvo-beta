from django.contrib import admin

from interactions.models import DrugInteraction


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = [
        "medicine_a",
        "medicine_b",
        "severity",
        "created_at",
    ]

    search_fields = [
        "medicine_a__name",
        "medicine_b__name",
        "description",
    ]

    list_filter = [
        "severity",
    ]