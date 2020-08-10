from rest_framework.serializers import ModelSerializer

from benchmarking_sessions.models import BenchmarkingSession


class BenchmarkingSessionSerializer(ModelSerializer):
    """Serializer for benchmark session data model"""

    class Meta:
        model = BenchmarkingSession
        fields = [
            "id",
            "case_set",
            "ai_implementations",
            "status",
            "created_on",
            "modified_on",
        ]


class BenchmarkingSessionResultsSerializer(ModelSerializer):
    """Serializer for benchmark session results"""

    class Meta:
        model = BenchmarkingSession
        fields = [
            "id",
            "case_set",
            "ai_implementations",
            "status",
            "responses",
        ]
