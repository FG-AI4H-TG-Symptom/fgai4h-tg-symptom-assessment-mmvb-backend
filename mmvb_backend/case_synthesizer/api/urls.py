from rest_framework.routers import DefaultRouter

from case_synthesizer.api.views import CaseSynthesizerViewSet
from case_synthesizer.apps import CaseSynthesizerConfig

app_name = CaseSynthesizerConfig.name

router = DefaultRouter(trailing_slash=False)
router.register(
    "case-synthesizer",
    CaseSynthesizerViewSet,
    basename="case-synthesizer",
)
