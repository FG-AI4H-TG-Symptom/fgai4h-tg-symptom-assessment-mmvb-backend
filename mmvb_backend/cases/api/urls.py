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

router.register(
    "cases",
    ExtendedCaseViewSet
    if "case_synthesizer" in settings.INSTALLED_APPS
    else CaseViewSet,
    basename="cases",
)
router.register(
    "case-sets",
    ExtendedCaseSetViewSet
    if "case_synthesizer" in settings.INSTALLED_APPS
    else CaseSetViewSet,
    basename="case-sets",
)
