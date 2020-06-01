from abc import ABC, abstractmethod

from django.shortcuts import get_object_or_404
from django.utils.decorators import classproperty

from benchmarking_sessions.models import BenchmarkingStepStatus
from cases.models import Case
from metrics.implementations.base import Metric


class CorrectConditionsTopN(Metric):
    @classproperty
    def name(cls):
        return "correct_conditions_top_n"

    @classproperty
    def description(cls):
        return "Correct conditions (top n)"

    @classmethod
    def _calculate_recall(cls, ai_result_conditions, correct_condition, top_n=None):
        return int(
            correct_condition["id"]
            in [condition["id"] for contition in ai_result_conditions[:top_n]]
        )

    @classmethod
    def calculate(cls, benchmarking_session_result, top_n=None):
        COMPLETED = BenchmarkingStepStatus.COMPLETED.value
        aggregated_metrics = {
            "id": cls.name,
            "name": cls.description,
            "values": []
        }

        cases_with_results_in_top_n = defaultdict(int)
        responses = benchmarking_session_result["responses"]
        for case_response in responses:
            # TODO: decide what to do if a case is not found
            case = get_object_or_404(Case, pk=case_response["caseId"])
            case_responses = case_response["responses"]

            for ai_implementation_id, response in case_responses.items():
                completed = response["status"] == COMPLETED
                result_conditions = response.get("conditions", [])
                correct_condition = case.data["valuesToPredict"]["condition"]

                ai_implementation_has_result_in_top_n = int(
                    completed and
                    cls._calculate_recall(
                        result_conditions,
                        correct_condition,
                        top_n,
                    )
                )

                cases_with_results_in_top_n[
                    ai_implementation_id
                ] += ai_implementation_has_result_in_top_n

        case_count = len(benchmarking_session_result["responses"])

        proportion_cases_with_ai_result_in_top_n = {
            ai_implementation_id: result_count / case_count
            for (ai_implementation_id, result_count)
            in cases_with_results_in_top_n.items()
        }

        aggregated_metrics["values"] = proportion_cases_with_ai_result_in_top_n
        return aggregated_metrics


class CorrectConditionsTop1(CorrectConditionsTopN):
    @classproperty
    def name(cls):
        return "correct_conditions_top_1"

    @classproperty
    def description(cls):
        return "Correct conditions (top 1)"

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        return super().calculate(benchmarking_session_result, top_n=1)


class CorrectConditionsTop3(CorrectConditionsTopN):
    @classproperty
    def name(cls):
        return "correct_conditions_top_3"

    @classproperty
    def description(cls):
        return "Correct conditions (top 3)"

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        return super().calculate(benchmarking_session_result, top_n=3)


class CorrectConditionsTop10(CorrectConditionsTopN):
    @classproperty
    def name(cls):
        return "correct_conditions_top_10"

    @classproperty
    def description(cls):
        return "Correct conditions (top 10)"

    @classmethod
    def calculate(cls, benchmarking_session_result, *args, **kwargs):
        return super().calculate(benchmarking_session_result, top_n=10)
