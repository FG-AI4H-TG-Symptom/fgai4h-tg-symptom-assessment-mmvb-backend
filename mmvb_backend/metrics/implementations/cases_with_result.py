from collections import defaultdict

from django.utils.decorators import classproperty

from benchmarking_sessions.models import BenchmarkingStepStatus
from metrics.implementations.base import Metric


class CasesWithAIResult(Metric):
    @classproperty
    def name(cls):
        return "cases_with_ai_result"

    @classproperty
    def description(cls):
        return "Cases with AI result"

    @classmethod
    def include_as_metric(cls):
        return True

    @classmethod
    def aggregate(cls, metrics):
        metrics["aggregatedValues"] = {}

        cases_with_ai_result_counts = defaultdict(int)
        for case_id, ais_metrics in metrics["values"]:
            for ai_implementation_id, has_result in ais_metrics.items():
                cases_with_ai_result_counts[ai_implementation_id] += has_result

        case_count = len(metrics["values"])
        proportion_cases_with_ai_result = {
            ai_implementation_id: result_count / case_count
            for (
                ai_implementation_id,
                result_count,
            ) in cases_with_ai_result_counts.items()
        }

        metrics["aggregatedValues"] = proportion_cases_with_ai_result
        return metrics

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        COMPLETED = BenchmarkingStepStatus.COMPLETED.value
        metrics = {"id": cls.name, "name": cls.description, "values": {}}

        cases_metrics = {}
        responses = benchmarking_session_result["responses"]
        for case_response in responses:
            case_id = case_response["caseId"]
            ai_responses = case_response["responses"]
            for ai_implementation_id, response in ai_responses.items():
                has_result_for_case = int(response["status"] == COMPLETED)

                cases_metrics.setdefault(case_id, {}).update(
                    {ai_implementation_id: has_result_for_case}
                )

        metrics["values"] = cases_metrics
        return metrics
