from rest_framework.serializers import IntegerField, Serializer


class CaseSynthesizerSerializer(Serializer):
    quantity = IntegerField()
