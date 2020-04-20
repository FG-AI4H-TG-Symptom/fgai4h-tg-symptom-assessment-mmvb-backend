# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.


SUPPORTED_METRICS = {
    "proportion_cases_with_ai_result": "Proportion of cases with AI result",
    "correct_conditions_top_1": "Correct conditions (top 1)",
    "correct_conditions_top_3": "Correct conditions (top 3)",
    "correct_conditions_top_10": "Correct conditions (top 10)",
    "triage_match": "Triage match",
    "triage_similarity": "Triage similarity",
    "triage_similarity_soft": "Soft triage similarity",
}

EXPECTED_TRIAGES = ["SC", "PC", "EC"]

SOFT_FAIL_TRIAGE_SIMILARITY = 0.2


def list_all_metrics():
    return {
        "metrics": [
            {"name": key, "human_name": value}
            for key, value in SUPPORTED_METRICS.items()
        ]
    }


def calculate_recall(ai_result_conditions, correct_condition, top_n=None):
    return float(
        correct_condition["id"]
        in [condition["id"] for condition in ai_result_conditions[:top_n]]
    )


def calculate_triage_similarity(expected_triage, ai_triage, soft=False):
    assert expected_triage in EXPECTED_TRIAGES
    if ai_triage not in EXPECTED_TRIAGES:
        if soft:
            return SOFT_FAIL_TRIAGE_SIMILARITY
        else:
            return 0.0

    expected_triage = EXPECTED_TRIAGES.index(expected_triage)
    ai_triage = EXPECTED_TRIAGES.index(ai_triage)

    return 1.0 - (
        abs(expected_triage - ai_triage) / (len(EXPECTED_TRIAGES) - 1.0)
    )


def calculate_metrics(request):
    metric_results = []

    for request_element in request:
        values_to_predict = request_element["valuesToPredict"]
        ai_result = request_element["aiResult"] or None

        if ai_result is None:
            ai_result_exists = 0.0
            triage_match = 0.0
            triage_similarity = 0.0
            triage_similarity_soft = 0.0
            recall_top_1 = 0.0
            recall_top_3 = 0.0
            recall_top_10 = 0.0
        else:
            ai_result_exists = 1.0

            recall_top_1 = calculate_recall(
                ai_result["conditions"],
                values_to_predict["condition"],
                top_n=1,
            )
            recall_top_3 = calculate_recall(
                ai_result["conditions"],
                values_to_predict["condition"],
                top_n=3,
            )
            recall_top_10 = calculate_recall(
                ai_result["conditions"],
                values_to_predict["condition"],
                top_n=10,
            )

            triage_match = float(
                values_to_predict["expectedTriageLevel"] == ai_result["triage"]
            )

            triage_similarity = calculate_triage_similarity(
                values_to_predict["expectedTriageLevel"], ai_result["triage"]
            )
            triage_similarity_soft = calculate_triage_similarity(
                values_to_predict["expectedTriageLevel"],
                ai_result["triage"],
                soft=True,
            )

        metric_results.append(
            {
                "proportion_cases_with_ai_result": ai_result_exists,
                "correct_conditions_top_1": recall_top_1,
                "correct_conditions_top_3": recall_top_3,
                "correct_conditions_top_10": recall_top_10,
                "triage_match": triage_match,
                "triage_similarity": triage_similarity,
                "triage_similarity_soft": triage_similarity_soft,
            }
        )

    return metric_results
