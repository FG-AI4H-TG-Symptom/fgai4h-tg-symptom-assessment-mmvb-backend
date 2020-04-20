from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ais.api.serializers import AIImplementationSerializer
from ais.models import AIImplementation
from common.utils import CamelCaseAutoSchema


# TODO: properly document endpoint
class AIImplementationViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=['AI Implementations',])
    serializer_class = AIImplementationSerializer

    def get_queryset(self):
        return AIImplementation.objects.all()

    @action(methods=["get"], detail=True, url_path="health-check")
    def health_check(self, request, *args, **kwargs):
        # TODO: implement actual endpoint
        return Response({}, status=status.HTTP_200_OK)
