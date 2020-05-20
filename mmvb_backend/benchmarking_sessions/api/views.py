from collections import defaultdict

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from benchmarking_sessions.api.serializers import (
    BenchmarkingSessionResultsSerializer,
    BenchmarkingSessionSerializer,
)
from benchmarking_sessions.api.utils import strip_values_from_responses
from benchmarking_sessions.models import (
    BenchmarkingSession,
    BenchmarkingStepStatus,
)
from benchmarking_sessions.tasks import run_benchmark
from celery.states import PENDING
from common.utils import CamelCaseAutoSchema


# todo: properly document endpoints
class BenchmarkingSessionViewSet(ModelViewSet):
    schema = CamelCaseAutoSchema(tags=["BenchmarkingSessions",])
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
            {
                "statusUrl": f"/benchmarking-sessions/{benchmarking_session.id}/status"
            },
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
        if result.status == PENDING or result.info is None:
            # this is an in-between state where the celery task status is not yet reflected in the main DB,
            # so either the task is about to begin or just finished -- in either case it's easiest to pretend it is
            # running
            return Response(
                {"status": BenchmarkingSession.Status.INTERMEDIATE},
                status=status.HTTP_200_OK,
            )

        strip_values_from_responses(result.info["responses"])

        return Response(
            {
                "status": BenchmarkingSession.Status.RUNNING,
                "report": result.info,
            },
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
        cases_with_ai_result_counts = defaultdict(int)
        responses = benchmarking_session_result["responses"]
        for case_response in responses:
            case_responses = case_response["responses"]
            for ai_implementation_id, response in case_responses.items():
                ai_implementation_has_result_for_case = int(
                    response["status"]
                    == BenchmarkingStepStatus.COMPLETED.value
                )
                cases_with_ai_result_counts[
                    ai_implementation_id
                ] += ai_implementation_has_result_for_case

        case_count = len(benchmarking_session_result["responses"])
        proportion_cases_with_ai_result = {
            ai_implementation_id: result_count / case_count
            for (
                ai_implementation_id,
                result_count,
            ) in cases_with_ai_result_counts.items()
        }

        benchmarking_session_result["aggregatedMetrics"] = [
            {
                "id": "proportion_cases_with_ai_result",
                "name": "Proportion of cases with AI result",
                "values": proportion_cases_with_ai_result,
            }
        ]

        return Response(
            benchmarking_session_result, status=status.HTTP_200_OK,
        )
