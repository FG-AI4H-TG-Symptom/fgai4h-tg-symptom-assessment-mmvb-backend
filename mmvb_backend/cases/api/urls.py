from django.conf import settings
from rest_framework.routers import DefaultRouter

from cases.api.views import CaseSetViewSet, CaseViewSet, ExtendedCaseViewSet
from cases.apps import CasesConfig

app_name = CasesConfig.name

router = DefaultRouter(trailing_slash=False)
if "case_synthesizer" in settings.INSTALLED_APPS:
    router.register("cases", ExtendedCaseViewSet, basename="cases")
else:
    router.register("cases", CaseViewSet, basename="cases")
router.register("case-sets", CaseSetViewSet, basename="case-sets")
