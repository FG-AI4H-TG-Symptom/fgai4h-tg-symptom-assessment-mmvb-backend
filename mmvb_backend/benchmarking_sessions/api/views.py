from benchmarking_sessions.api.serializers import (
    BenchmarkingSessionResultsSerializer,
    BenchmarkingSessionSerializer,
)
from benchmarking_sessions.api.utils import strip_values_from_responses
from benchmarking_sessions.models import BenchmarkingSession
from benchmarking_sessions.tasks import run_benchmark
from celery.states import PENDING
from common.utils import CamelCaseAutoSchema
from django.shortcuts import get_object_or_404
from metrics.helpers import calculate_metrics
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


# todo: properly document endpoints
class BenchmarkingSessionViewSet(ModelViewSet):
    """ViewSet for handling benchmark session requests"""

    schema = CamelCaseAutoSchema(tags=["BenchmarkingSessions",])
    serializer_class = BenchmarkingSessionSerializer

    def get_queryset(self):
        return BenchmarkingSession.objects.all()

    # todo: generate 404
    @action(methods=["post"], detail=True, url_path="run")
    def run_benchmark(self, request, *args, **kwargs):
        """Handler for running benchmark sessions"""
        benchmarking_session = get_object_or_404(
            BenchmarkingSession, id=kwargs["pk"]
        )

        # pushes benchmarking task into celery queue
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
        """Handler for checking benchmark session status"""
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
        """Handler for fetching benchmark results"""
        benchmarking_session = get_object_or_404(
            BenchmarkingSession, id=kwargs["pk"]
        )

        benchmarking_session_result = BenchmarkingSessionResultsSerializer(
            benchmarking_session
        ).data

        # calculates and aggregates metrics for benchmark results
        benchmarking_session_result["metrics"] = calculate_metrics(
            benchmarking_session_result
        )

        return Response(
            benchmarking_session_result, status=status.HTTP_200_OK,
        )
