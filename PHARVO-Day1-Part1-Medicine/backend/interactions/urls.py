from django.urls import path, include
from rest_framework.routers import DefaultRouter

from interactions.views import (
    DrugInteractionViewSet,
)


router = DefaultRouter()

router.register(
    r"drug-interactions",
    DrugInteractionViewSet,
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]