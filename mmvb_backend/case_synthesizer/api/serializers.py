from django.urls import reverse
from rest_framework.serializers import BaseSerializer, IntegerField, Serializer

from case_synthesizer.validators import quantity_range


class CaseSynthesizerSerializer(Serializer):
    quantity = IntegerField(validators=[quantity_range])


class CasesListSerializer(BaseSerializer):
    def to_representation(self, obj):
        return reverse("cases-detail", kwargs={"pk": obj.pk})

    def to_internal_value(self, data):
        return {"quantity": data["quantity"]}
