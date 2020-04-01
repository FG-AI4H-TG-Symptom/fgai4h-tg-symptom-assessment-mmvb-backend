from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ais.apps import AisConfig
from ais.api.views import AIImplementationViewSet

app_name = AisConfig.name

router = DefaultRouter()
router.register(
    "ai-implementations", AIImplementationViewSet, basename="ai-implementations"
)
