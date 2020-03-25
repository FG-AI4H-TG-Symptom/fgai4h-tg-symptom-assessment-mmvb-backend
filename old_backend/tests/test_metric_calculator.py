from deepdiff import DeepDiff

from metric_calculator import api

TEST_CASES = [
    {
        "input": {
            "valuesToPredict": {"condition": {"id": "b"}, "expectedTriageLevel": "PC"},
            "aiResult": {
                "conditions": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
                "triage": "SC",
            },
        },
        "output": {
            "correct_conditions_top_1": 0.0,
            "correct_conditions_top_3": 1.0,
            "correct_conditions_top_10": 1.0,
            "proportion_cases_with_ai_result": 1.0,
            "triage_match": 0.0,
            "triage_similarity": 0.5,
            "triage_similarity_soft": 0.5,
        },
    },
    {
        "input": {
            "valuesToPredict": {"condition": {"id": "a"}, "expectedTriageLevel": "PC"},
            "aiResult": {
                "conditions": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
                "triage": "PC",
            },
        },
        "output": {
            "correct_conditions_top_1": 1.0,
            "correct_conditions_top_3": 1.0,
            "correct_conditions_top_10": 1.0,
            "proportion_cases_with_ai_result": 1.0,
            "triage_match": 1.0,
            "triage_similarity": 1.0,
            "triage_similarity_soft": 1.0,
        },
    },
    {
        "input": {
            "valuesToPredict": {"condition": {"id": "d"}, "expectedTriageLevel": "PC"},
            "aiResult": {
                "conditions": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
                "triage": "SC",
            },
        },
        "output": {
            "correct_conditions_top_1": 0.0,
            "correct_conditions_top_3": 0.0,
            "correct_conditions_top_10": 0.0,
            "proportion_cases_with_ai_result": 1.0,
            "triage_match": 0.0,
            "triage_similarity": 0.5,
            "triage_similarity_soft": 0.5,
        },
    },
]


def test_calculate_metrics():
    test_case_input = [test_case["input"] for test_case in TEST_CASES]
    test_case_output = [test_case["output"] for test_case in TEST_CASES]
    res = api.calculate_metrics(test_case_input)
    assert DeepDiff(res, test_case_output) == dict()
