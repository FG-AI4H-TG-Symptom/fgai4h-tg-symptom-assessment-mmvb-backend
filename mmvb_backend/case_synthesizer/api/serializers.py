from rest_framework.serializers import Serializer, IntegerField


class CaseSynthesizerSerializer(Serializer):
    quantity = IntegerField()
