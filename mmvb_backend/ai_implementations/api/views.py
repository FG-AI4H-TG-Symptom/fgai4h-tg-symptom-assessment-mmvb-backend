from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ai_implementations.api.serializers import AIImplementationSerializer
from ai_implementations.models import AIImplementation
from common.utils import CamelCaseAutoSchema, perform_request


# TODO: properly document endpoint
class AIImplementationViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=["AI Implementations",])
    serializer_class = AIImplementationSerializer

    def get_queryset(self):
        return AIImplementation.objects.all()

    @action(methods=["get"], detail=True, url_path="health-check")
    def health_check(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        ai_implementation = self.get_queryset().filter(pk=pk).first()

        if ai_implementation is None:
            response_status = status.HTTP_404_NOT_FOUND
            response_data = {
                "status": None,
                "data": None,
                "detail": f"Could not find ai implementation with id {pk}",
            }
        else:
            response_status = status.HTTP_200_OK
            target_url = f"{ai_implementation.base_url}/health-check"
            response_data = perform_request(target_url)

        return Response(response_data, status=response_status)
