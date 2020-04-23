from rest_framework.viewsets import ModelViewSet

from cases.api.serializers import (
    CaseSerializer,
    CaseSetFullSerializer,
    CaseSetSerializer,
)
from cases.models import Case, CaseSet
from common.utils import CamelCaseAutoSchema, is_true


# TODO: properly document endpoints
class CaseViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=["Cases",])
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.all().order_by("id")


class CaseSetViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=["Cases",])
    serializer_class = CaseSetSerializer

    def get_queryset(self):
        return CaseSet.objects.all()

    def retrieve(self, request, *args, **kwargs):
        full = request.query_params.get("full", False)
        if is_true(full):
            self.serializer_class = CaseSetFullSerializer
        return super().retrieve(request, *args, **kwargs)
