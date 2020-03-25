from rest_framework.serializers import ModelSerializer

from ais.models import AIImplementation


class AIImplementationSerializer(ModelSerializer):
    class Meta:
        model = AIImplementation
        fields = [
            "id",
            "name",
            "base_url",
            "health_endpoint",
            "solution_endpoint"
        ]
