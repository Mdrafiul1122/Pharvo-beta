from django.urls import path, include
from .views import ai_query

urlpatterns = [
    path("query/", ai_query, name="ai-query"),
    path("api/ai/", include("ai_service.urls")),
]