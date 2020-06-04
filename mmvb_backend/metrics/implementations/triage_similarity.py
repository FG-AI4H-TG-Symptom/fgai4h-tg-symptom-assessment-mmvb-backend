from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.utils.decorators import classproperty

from benchmarking_sessions.models import BenchmarkingStepStatus
from cases.models import Case
from common.definitions import (
    EXPECTED_TRIAGE_OPTIONS,
    SOFT_FAIL_TRIAGE_SIMILARITY,
)
from metrics.implementations.base import Metric


class TriageSimilarityBase(Metric):
    @classproperty
    def name(cls):
        return "triage_similarity_base"

    @classproperty
    def description(cls):
        return "Triage similarity (Base)"

    @classmethod
    def include_as_metric(cls):
        return False

    def _calculate_triage_similarity(expected_triage, ai_triage, soft=False):
        # TODO: what to do in case this validation fails?
        assert expected_triage in EXPECTED_TRIAGE_OPTIONS
        if ai_triage not in EXPECTED_TRIAGE_OPTIONS:
            if soft:
                return SOFT_FAIL_TRIAGE_SIMILARITY
            else:
                return 0.0

        expected_triage = EXPECTED_TRIAGE_OPTIONS.index(expected_triage)
        ai_triage = EXPECTED_TRIAGE_OPTIONS.index(ai_triage)

        similarity_factor = abs(expected_triage - ai_triage) / (
            len(EXPECTED_TRIAGE_OPTIONS) - 1.0
        )

        return 1.0 - similarity_factor

    @classmethod
    def aggregate(cls, metrics):
        metrics["aggregatedValues"] = {}

        ais_triage_similarity_sum = defaultdict(int)
        for case_id, ais_metrics in metrics["values"].items():
            for ai_implementation_id, triage_similarity in ais_metrics.items():
                ais_triage_similarity_sum[
                    ai_implementation_id
                ] += triage_similarity

        case_count = len(metrics["values"])
        mean_triage_similarity = {
            ai_implementation_id: similarity_sum / case_count
            for (
                ai_implementation_id,
                similarity_sum,
            ) in ais_triage_similarity_sum.items()
        }

        metrics["aggregatedValues"] = mean_triage_similarity
        return metrics

    @classmethod
    def calculate(cls, benchmarking_session_result, soft=False):
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

                if not has_completed:
                    triage_similarity = 0.0
                else:
                    expected_triage = case.data["valuesToPredict"][
                        "expectedTriageLevel"
                    ]

                    triage_similarity = cls._calculate_triage_similarity(
                        expected_triage, response.get("triage", ""), soft=soft
                    )

                cases_metrics.setdefault(case_id, {}).update(
                    {ai_implementation_id: triage_similarity}
                )

        metrics["values"] = cases_metrics
        return metrics


class TriageSimilarity(TriageSimilarityBase):
    @classproperty
    def name(cls):
        return "triage_similarity"

    @classproperty
    def description(cls):
        return "Triage similarity"

    @classmethod
    def include_as_metric(cls):
        return True

    @classmethod
    def calculate(cls, benchmarking_session_result):
        return super().calculate(benchmarking_session_result, soft=False)


class SoftTriageSimilarity(TriageSimilarityBase):
    @classproperty
    def name(cls):
        return "soft_triage_similarity"

    @classproperty
    def description(cls):
        return "Soft triage similarity"

    @classmethod
    def include_as_metric(cls):
        return True

    @classmethod
    def calculate(cls, benchmarking_session_result):
        return super().calculate(benchmarking_session_result, soft=True)
