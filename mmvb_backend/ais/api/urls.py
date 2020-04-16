from django.urls import include, path

from ais.api.views import AIImplementationViewSet
from ais.apps import AisConfig
from rest_framework.routers import DefaultRouter

app_name = AisConfig.name

router = DefaultRouter()
router.register(
    "ai-implementations",
    AIImplementationViewSet,
    basename="ai-implementations",
)
