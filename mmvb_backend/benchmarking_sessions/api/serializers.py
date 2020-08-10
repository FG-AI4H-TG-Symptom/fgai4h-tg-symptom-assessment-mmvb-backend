from benchmarking_sessions.models import BenchmarkingSession
from rest_framework.serializers import ModelSerializer


class BenchmarkingSessionSerializer(ModelSerializer):
    """Serializer for benchmark session data model"""

    class Meta:
        model = BenchmarkingSession
        fields = ["id", "case_set", "ai_implementations", "status"]


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
