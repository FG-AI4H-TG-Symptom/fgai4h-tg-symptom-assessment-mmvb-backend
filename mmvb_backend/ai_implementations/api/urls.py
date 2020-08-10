from ai_implementations.api.views import AIImplementationViewSet
from ai_implementations.apps import AisConfig
from rest_framework.routers import DefaultRouter

app_name = AisConfig.name

# registers route for ai implementations
router = DefaultRouter(trailing_slash=False)
router.register(
    "ai-implementations",
    AIImplementationViewSet,
    basename="ai-implementations",
)
