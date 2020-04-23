from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet

from case_synthesizer.api.schemas import CaseSynthesizerSchema
from case_synthesizer.api.serializers import CaseSynthesizerSerializer
from case_synthesizer.generator import generate_cases
from cases.api.serializers import CaseSerializer


class CaseSynthesizerViewSet(GenericViewSet):
    schema = CaseSynthesizerSchema(
        tags=["Case Synthesizer"], operation_id_base="synthesizeCases"
    )
    serializer_class = CaseSynthesizerSerializer

    def get_response_serializer(self, *args, **kwargs):
        serializer_class = CaseSerializer
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data.get("quantity")
            cases = generate_cases(int(quantity))
            serializer = CaseSerializer(cases, many=True)
            return Response(data=serializer.data, status=HTTP_201_CREATED)
        else:
            error = {"quantity": str(serializer.errors["quantity"][0])}
            return Response(
                data={"detail": error}, status=HTTP_400_BAD_REQUEST
            )
