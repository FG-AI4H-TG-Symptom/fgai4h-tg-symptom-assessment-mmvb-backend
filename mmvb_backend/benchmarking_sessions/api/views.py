from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ModelViewSet

from benchmarking_sessions.api.serializers import (
    BenchmarkingSessionResultsSerializer,
    BenchmarkingSessionSerializer,
)
from benchmarking_sessions.models import (
    BenchmarkingSession,
    BenchmarkingStepStatus,
)
from benchmarking_sessions.tasks import run_benchmark


# todo: properly document endpoints
class BenchmarkingSessionViewSet(ModelViewSet):
    schema = AutoSchema(tags=["BenchmarkingSessions",])
    serializer_class = BenchmarkingSessionSerializer

    def get_queryset(self):
        return BenchmarkingSession.objects.all()

    # todo: generate 404
    @action(methods=["post"], detail=True, url_path="run")
    def run_benchmark(self, request, *args, **kwargs):
        benchmarking_session = get_object_or_404(
            BenchmarkingSession, id=kwargs["pk"]
        )
        task = run_benchmark.delay(benchmarking_session.id)
        benchmarking_session.task_id = task.id
        benchmarking_session.save()
        return Response(
            f"/benchmarking-sessions/{benchmarking_session.id}/status",
            status=status.HTTP_202_ACCEPTED,
        )

    # todo: document response structure (OpenAPI)
    @action(methods=["get"], detail=True, url_path="status")
    def benchmark_status(self, request, *args, **kwargs):
        benchmarking_session = get_object_or_404(
            BenchmarkingSession, id=kwargs["pk"]
        )
        if benchmarking_session.status != BenchmarkingSession.Status.RUNNING:
            return Response(
                {"status": benchmarking_session.status},
                status=status.HTTP_200_OK,
            )

        result = run_benchmark.AsyncResult(benchmarking_session.task_id)
        if result.status == "PENDING" or result.info is None:
            # this is an in-between state where the celery task status is not yet reflected in the main DB,
            # so either the task is about to begin or just finished -- in either case it's easiest to pretend it is
            # running
            return Response(
                {"status": BenchmarkingSession.Status.INTERMEDIATE},
                status=status.HTTP_200_OK,
            )

        for case_responses in result.info["responses"]:
            for ai_implementation_id, response in case_responses[
                "responses"
            ].items():
                if "value" in response:
                    del response["value"]

        return Response(
            {"status": BenchmarkingSession.Status.RUNNING, "report": result.info},
            status=status.HTTP_200_OK,
        )

    # todo: document response structure (OpenAPI)
    @action(methods=["get"], detail=True, url_path="results")
    def benchmark_results(self, request, *args, **kwargs):
        benchmarking_session = get_object_or_404(
            BenchmarkingSession, id=kwargs["pk"]
        )

        benchmarking_session_result = BenchmarkingSessionResultsSerializer(
            benchmarking_session
        ).data

        # todo: add metrics infrastructure, add more metrics
        proportion_cases_with_ai_result_counts = {}
        for case_response in benchmarking_session_result["responses"]:
            for ai_implementation_id, response in case_response[
                "responses"
            ].items():
                proportion_cases_with_ai_result_counts[
                    ai_implementation_id
                ] = proportion_cases_with_ai_result_counts.get(
                    ai_implementation_id, 0
                ) + int(
                    response["status"]
                    == BenchmarkingStepStatus.COMPLETED.value
                )

        proportion_cases_with_ai_result_values = {}
        for (
            ai_implementation_id,
            proportion_cases_with_ai_result_count,
        ) in proportion_cases_with_ai_result_counts.items():
            proportion_cases_with_ai_result_values[ai_implementation_id] = (
                proportion_cases_with_ai_result_count
                / len(benchmarking_session_result["responses"])
            )

        benchmarking_session_result["aggregatedMetrics"] = {
            "proportion_cases_with_ai_result": {
                "id": "proportion_cases_with_ai_result",
                "name": "Proportion of cases with AI result",
                "values": proportion_cases_with_ai_result_values,
            }
        }

        return Response(
            benchmarking_session_result, status=status.HTTP_200_OK,
        )
