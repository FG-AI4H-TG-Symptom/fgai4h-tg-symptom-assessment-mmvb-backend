from django.urls import reverse
from rest_framework.serializers import BaseSerializer, IntegerField, Serializer

from case_synthesizer.validators import (
    MAX_CASES_QUANTITY,
    MAX_CASESETS_QUANTITY,
    MIN_CASES_QUANTITY,
    MIN_CASESETS_QUANTITY,
    quantity_range,
)


class CaseSynthesizerSerializer(Serializer):
    quantity = IntegerField(
        validators=[quantity_range(MIN_CASES_QUANTITY, MAX_CASES_QUANTITY)]
    )


class CaseSetSynthesizerSerializer(Serializer):
    cases_per_caseset = IntegerField(
        validators=[quantity_range(MIN_CASES_QUANTITY, MAX_CASES_QUANTITY)]
    )
    quantity_of_casesets = IntegerField(
        validators=[quantity_range(MIN_CASESETS_QUANTITY, MAX_CASESETS_QUANTITY)])


class CasesListSerializer(BaseSerializer):
    def to_representation(self, obj):
        return reverse("cases-detail", kwargs={"pk": obj.pk})

    def to_internal_value(self, data):
        return {"quantity": data["quantity"]}
