from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.utils.decorators import classproperty

from benchmarking_sessions.models import BenchmarkingStepStatus
from cases.models import Case
from metrics.implementations.base import Metric


class TriageMatch(Metric):
    @classproperty
    def name(cls):
        return "triage_match"

    @classproperty
    def description(cls):
        return "Triage match"

    @classmethod
    def aggregate(cls, metrics):
        metrics["aggregatedValues"] = {}

        ais_with_triage_match = defaultdict(int)
        for case_id, ais_metrics in metrics["values"].items():
            for ai_implementation_id, triage_matches in ais_metrics.items():
                ais_with_triage_match[ai_implementation_id] += triage_matches

        case_count = len(metrics["values"])
        proportion_cases_with_triage_match = {
            ai_implementation_id: result_count / case_count
            for (
                ai_implementation_id,
                result_count,
            ) in ais_with_triage_match.items()
        }

        metrics["aggregatedValues"] = proportion_cases_with_triage_match
        return metrics

    @classmethod
    def calculate(cls, benchmarking_session_result):
        COMPLETED = BenchmarkingStepStatus.COMPLETED.value
        metrics = {"id": cls.name, "name": cls.description, "values": {}}

        cases_metrics = {}
        responses = benchmarking_session_result["responses"]
        for case_response in responses:
            case_id = case_response["caseId"]
            case = get_object_or_404(Case, pk=case_id)

            ai_responses = case_response["responses"]
            for ai_implementation_id, response in ai_responses.items():
                has_completed = response["status"] == COMPLETED
                expected_triage = case.data["valuesToPredict"][
                    "expectedTriageLevel"
                ]
                triage_matches = int(
                    has_completed
                    and response.get("triage", "") == expected_triage
                )

                cases_metrics.setdefault(case_id, {}).update(
                    {ai_implementation_id: triage_matches}
                )

        metrics["values"] = cases_metrics
        return metrics
