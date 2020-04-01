from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cases.apps import CasesConfig
from cases.api.views import CaseViewSet, CaseSetViewSet

app_name = CasesConfig.name

router = DefaultRouter()
router.register(
    "cases", CaseViewSet, basename="cases"
)
router.register(
    "case-sets", CaseSetViewSet, basename="case-sets"
)
