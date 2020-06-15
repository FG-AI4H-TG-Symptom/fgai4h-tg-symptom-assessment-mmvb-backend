from rest_framework import status
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.viewsets import ViewSet

from metrics.implementations import SUPPORTED_METRICS


class MetricsViewset(ViewSet):
    """ViewSet for handling Metrics requests"""

    schema = AutoSchema(tags=["Metrics"])

    def list(self, request):
        """Handles the request for the available metrics list"""
        metrics_data = [
            {"id": name, "name": metric.description}
            for (name, metric) in SUPPORTED_METRICS.items()
        ]
        return Response(metrics_data, status.HTTP_200_OK)
