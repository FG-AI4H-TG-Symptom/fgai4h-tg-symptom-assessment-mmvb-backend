from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.utils.decorators import classproperty

from benchmarking_sessions.models import BenchmarkingStepStatus
from cases.models import Case
from metrics.implementations.base import Metric


class CorrectConditionsTop1(Metric):
    @classproperty
    def name(cls):
        return "correct_conditions_top_1"

    @classproperty
    def description(cls):
        return "Correct conditions (top 1)"

    @classmethod
    def _calculate_recall(
        cls, ai_result_conditions, correct_condition, top_n=None
    ):
        return int(
            correct_condition["id"]
            in [condition["id"] for condition in ai_result_conditions[:top_n]]
        )

    @classmethod
    def aggregate(cls, metrics):
        metrics["aggregatedValues"] = {}

        ais_with_results_in_top_n = defaultdict(int)
        for case_id, ais_metrics in metrics["values"]:
            for ai_implementation_id, has_result in ais_metrics.items():
                ais_with_results_in_top_n[ai_implementation_id] += has_result

        case_count = len(metrics["values"])
        proportion_cases_with_results_in_top_n = {
            ai_implementation_id: result_count / case_count
            for (
                ai_implementation_id,
                result_count,
            ) in ais_with_results_in_top_n.items()
        }

        metrics["aggregatedValues"] = proportion_cases_with_results_in_top_n
        return metrics

    @classmethod
    def calculate(cls, benchmarking_session_result, top_n=1):
        COMPLETED = BenchmarkingStepStatus.COMPLETED.value
        metrics = {"id": cls.name, "name": cls.description, "values": {}}

        cases_metrics = {}
        responses = benchmarking_session_result["responses"]
        for case_response in responses:
            case_id = case_response["caseId"]
            case = get_object_or_404(Case, pk=case_id)

            ai_responses = case_response["responses"]
            for ai_implementation_id, response in ai_responses.items():
                completed = response["status"] == COMPLETED
                result_conditions = response.get("conditions", [])
                correct_condition = case.data["valuesToPredict"]["condition"]

                has_result_in_top_n = int(
                    completed
                    and cls._calculate_recall(
                        result_conditions, correct_condition, top_n=top_n
                    )
                )

                cases_metrics.setdefault(case_id, {}).update(
                    {ai_implementation_id: has_result_in_top_n}
                )
        metrics["values"] = cases_metrics
        return metrics


class CorrectConditionsTop3(CorrectConditionsTop1):
    @classproperty
    def name(cls):
        return "correct_conditions_top_3"

    @classproperty
    def description(cls):
        return "Correct conditions (top 3)"

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        return super().calculate(benchmarking_session_result, top_n=3)


class CorrectConditionsTop10(CorrectConditionsTop1):
    @classproperty
    def name(cls):
        return "correct_conditions_top_10"

    @classproperty
    def description(cls):
        return "Correct conditions (top 10)"

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        return super().calculate(benchmarking_session_result, top_n=10)
