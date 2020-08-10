from rest_framework.routers import DefaultRouter

from metrics.api.views import MetricsViewset
from metrics.apps import MetricsConfig

app_name = MetricsConfig.name

# Routes the metrics endpoint for the correct request handler (view)
router = DefaultRouter()
router.register("metrics", MetricsViewset, basename="metrics")
