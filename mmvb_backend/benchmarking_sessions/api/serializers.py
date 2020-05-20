from rest_framework.serializers import ModelSerializer

from benchmarking_sessions.models import BenchmarkingSession


class BenchmarkingSessionSerializer(ModelSerializer):
    class Meta:
        model = BenchmarkingSession
        fields = ["id", "case_set", "ai_implementations", "status"]


class BenchmarkingSessionResultsSerializer(ModelSerializer):
    class Meta:
        model = BenchmarkingSession
        fields = [
            "id",
            "case_set",
            "ai_implementations",
            "status",
            "responses",
        ]
