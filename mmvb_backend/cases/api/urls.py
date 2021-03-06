from django.conf import settings
from rest_framework.routers import DefaultRouter

from cases.api.views import (
    CaseSetViewSet,
    CaseViewSet,
    ExtendedCaseSetViewSet,
    ExtendedCaseViewSet,
)
from cases.apps import CasesConfig

app_name = CasesConfig.name

router = DefaultRouter(trailing_slash=False)

# conditionally registers the viewsets according to the settings
# enabling or not case synthetization features
router.register(
    "cases",
    ExtendedCaseViewSet if settings.ENABLE_CASE_SYNTHESIZER else CaseViewSet,
    basename="cases",
)
router.register(
    "case-sets",
    ExtendedCaseSetViewSet
    if settings.ENABLE_CASE_SYNTHESIZER
    else CaseSetViewSet,
    basename="case-sets",
)
