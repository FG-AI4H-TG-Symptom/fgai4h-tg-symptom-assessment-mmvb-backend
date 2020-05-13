from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from case_synthesizer.api.schemas import (
    CaseSetSynthesizerSchema,
    CaseSynthesizerSchema,
)
from case_synthesizer.api.serializers import (
    CaseSetSynthesizerSerializer,
    CasesListSerializer,
    CaseSynthesizerSerializer,
)
from case_synthesizer.generator import generate_cases, generate_casesets
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


class ExtendedCaseViewSet(CaseViewSet):
    def get_serializer_class(self):
        if self.action == "synthesize":
            return CaseSynthesizerSerializer
        else:
            return CaseSerializer

    def get_response_serializer(self, *args, **kwargs):
        serializer_class = CasesListSerializer
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    @action(
        methods=["post"],
        detail=False,
        schema=CaseSynthesizerSchema(
            tags=["Cases"], operation_id_base="synthesizeCases"
        ),
        url_path="synthesize",
    )
    def synthesize(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data.get("quantity")
            cases = generate_cases(int(quantity))
            serialized = CasesListSerializer(cases, many=True)
            return Response(data=serialized.data, status=HTTP_201_CREATED)
        else:
            error = {"quantity": str(serializer.errors["quantity"][0])}
            return Response(
                data={"detail": error}, status=HTTP_400_BAD_REQUEST
            )


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


class ExtendedCaseSetViewSet(CaseSetViewSet):
    def get_serializer_class(self):
        if self.action == "synthesize":
            return CaseSetSynthesizerSerializer
        else:
            return CaseSetSerializer

    def get_response_serializer(self, *args, **kwargs):
        serializer_class = CaseSetSerializer
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    @action(
        methods=["post"],
        detail=False,
        schema=CaseSetSynthesizerSchema(
            tags=["Cases"], operation_id_base="synthesizeCaseSets"
        ),
        url_path="synthesize",
    )
    def synthesize(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            cases_per_caseset = serializer.validated_data.get(
                "cases_per_caseset"
            )
            quantity_of_casesets = serializer.validated_data.get(
                "quantity_of_casesets"
            )

            case_sets = generate_casesets(
                quantity_of_casesets, cases_per_caseset
            )

            serialized = CaseSetSerializer(case_sets, many=True)
            return Response(data=serialized.data, status=HTTP_201_CREATED)
        else:
            errors = {}

            cases_per_caseset = serializer.errors.get(
                "cases_per_caseset", None
            )
            if cases_per_caseset:
                errors["cases_per_caseset"] = str(cases_per_caseset[0])

            quantity_of_casesets = serializer.errors.get(
                "quantity_of_casesets", None
            )
            if quantity_of_casesets:
                errors["quantity_of_casesets"] = str(quantity_of_casesets[0])

            return Response(
                data={"detail": errors}, status=HTTP_400_BAD_REQUEST
            )
