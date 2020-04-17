from rest_framework.routers import DefaultRouter

from cases.api.views import CaseSetViewSet, CaseViewSet
from cases.apps import CasesConfig

app_name = CasesConfig.name

router = DefaultRouter()
router.register("cases", CaseViewSet, basename="cases")
router.register("case-sets", CaseSetViewSet, basename="case-sets")
