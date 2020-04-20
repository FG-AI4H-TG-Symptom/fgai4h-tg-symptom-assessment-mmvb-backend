from rest_framework.routers import DefaultRouter

from ais.api.views import AIImplementationViewSet
from ais.apps import AisConfig

app_name = AisConfig.name

router = DefaultRouter()
router.register(
    "ai-implementations",
    AIImplementationViewSet,
    basename="ai-implementations",
)
