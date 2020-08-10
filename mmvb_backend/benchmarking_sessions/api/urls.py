from benchmarking_sessions.api.views import BenchmarkingSessionViewSet
from benchmarking_sessions.apps import BenchmarkingSessionsConfig
from rest_framework.routers import DefaultRouter

app_name = BenchmarkingSessionsConfig.name

# Routes benchmarking sessions requests to the proper handler
router = DefaultRouter()
router.register(
    "benchmarking-sessions",
    BenchmarkingSessionViewSet,
    basename="benchmarking-sessions",
)
