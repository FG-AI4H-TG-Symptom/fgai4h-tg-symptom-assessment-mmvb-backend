from rest_framework.routers import DefaultRouter

from ai_implementations.api.views import AIImplementationViewSet
from ai_implementations.apps import AisConfig

app_name = AisConfig.name

router = DefaultRouter(trailing_slash=False)
router.register(
    "ai-implementations",
    AIImplementationViewSet,
    basename="ai-implementations",
)
