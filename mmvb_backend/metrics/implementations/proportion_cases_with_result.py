from django.utils.decorators import classproperty

from benchmarking_sessions.models import BenchmarkingStepStatus
from metrics.implementations.base import Metric


class ProportionOfCasesWithAIResult(Metric):
    @classproperty
    def name(cls):
        return "proportion_cases_with_ai_result"

    @classproperty
    def description(cls):
        return "Proportion of cases with AI result"

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        COMPLETED = BenchmarkingStepStatus.COMPLETED.value
        aggregated_metrics = {
            "id": cls.name,
            "name": cls.description,
            "values": []
        }

        cases_with_ai_result_counts = defaultdict(int)
        responses = benchmarking_session_result["responses"]
        for case_response in responses:
            case_responses = case_response["responses"]
            for ai_implementation_id, response in case_responses.items():
                ai_implementation_has_result_for_case = int(
                    response["status"] == COMPLETED
                )
                cases_with_ai_result_counts[
                    ai_implementation_id
                ] += ai_implementation_has_result_for_case

        case_count = len(benchmarking_session_result["responses"])
        proportion_cases_with_ai_result = {
            ai_implementation_id: result_count / case_count
            for (ai_implementation_id, result_count)
            in cases_with_ai_result_counts.items()
        }

        aggregated_metrics["values"] = proportion_cases_with_ai_result
        return aggregated_metrics
