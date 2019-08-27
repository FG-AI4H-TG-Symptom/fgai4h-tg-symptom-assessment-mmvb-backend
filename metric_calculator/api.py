# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.


SUPPORTED_METRICS = {
    "correct_conditions_top_1": "Correct conditions (top 1)",
    "correct_conditions_top_3": "Correct conditions (top 3)",
    "correct_conditions_top_10": "Correct conditions (top 10)",
    "triage_match": "Triage match",
}


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


def calculate_metrics(request):
    metric_results = []

    for request_element in request:
        values_to_predict = request_element["valuesToPredict"]
        ai_result = request_element["aiResult"]

        if ai_result is None:
            triage_match = 0.0
            recall_top_1 = 0.0
            recall_top_3 = 0.0
            recall_top_10 = 0.0
        else:
            recall_top_1 = calculate_recall(
                ai_result["conditions"], values_to_predict["condition"], top_n=1
            )
            recall_top_3 = calculate_recall(
                ai_result["conditions"], values_to_predict["condition"], top_n=3
            )
            recall_top_10 = calculate_recall(
                ai_result["conditions"], values_to_predict["condition"], top_n=10
            )

            triage_match = float(
                values_to_predict["expectedTriageLevel"] == ai_result["triage"]
            )

        metric_results.append(
            {
                "correct_conditions_top_1": recall_top_1,
                "correct_conditions_top_3": recall_top_3,
                "correct_conditions_top_10": recall_top_10,
                "triage_match": triage_match,
            }
        )

    return metric_results
