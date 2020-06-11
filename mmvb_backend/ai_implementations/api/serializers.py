from rest_framework.serializers import ModelSerializer

from ai_implementations.models import AIImplementation


class AIImplementationSerializer(ModelSerializer):
    """Serializer for AI Implementation data model"""

    class Meta:
        model = AIImplementation
        fields = ["id", "name", "base_url"]
