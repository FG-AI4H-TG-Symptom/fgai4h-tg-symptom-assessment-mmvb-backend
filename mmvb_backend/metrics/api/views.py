from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.schemas.openapi import AutoSchema

from metrics.implementations import SUPPORTED_METRICS


class MetricsViewset(ViewSet):
    schema = AutoSchema(tags=["Metrics"])
    def list(self, request):
        metrics_data = [
            {
                "id": name,
                "name": metric.description
            }
            for (name, metric) in SUPPORTED_METRICS.items()
        ]
        return Response(metrics_data, status.HTTP_200_OK)
