from django.urls import reverse

from case_synthesizer.validators import quantity_range
from rest_framework.serializers import IntegerField, Serializer, BaseSerializer


class CaseSynthesizerSerializer(Serializer):
    quantity = IntegerField(validators=[quantity_range])


class CasesListSerializer(BaseSerializer):
    def to_representation(self, obj):
        return reverse("cases-detail", kwargs={"pk": obj.pk})
