from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ModelViewSet

from cases.api.serializers import CaseSerializer, CaseSetSerializer
from cases.models import Case, CaseSet
from common.utils import CamelCaseAutoSchema


# TODO: properly document endpoints
class CaseViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=['Cases',])
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.all()


class CaseSetViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=['Cases',])
    serializer_class = CaseSetSerializer

    def get_queryset(self):
        return CaseSet.objects.all()
