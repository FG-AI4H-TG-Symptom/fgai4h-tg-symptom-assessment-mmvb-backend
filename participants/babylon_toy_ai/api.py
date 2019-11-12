# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import json
import os
import random

import numpy

from toy_ai.utils import (solve_case_error_type_one,
                          solve_case_error_type_two,
                          solve_case_soft_timeout,
                          solve_case_hard_timeout)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_RETURNED_CONDITIONS = 7


def drop_all_but_keys(val, keys):
    output = {}
    for key in keys:
        output[key] = val[key]
    return output


DATA = json.load(open(os.path.join(ROOT_DIR, "data", "data.json")))


def extract_biological_sex(case_data):
    biological_sex = case_data["profileInformation"]["biologicalSex"]
    assert biological_sex in ["male", "female"]
    return biological_sex


# https://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list
def sort_array_by_another_array(values, map_for_ordering, reverse=False):
    return [
        element
        for _, element in sorted(
            zip(map_for_ordering, values), key=lambda pair: pair[0], reverse=reverse
        )
    ]


def solve_case_by_symptom_intersection(case_data):
    biological_sex = extract_biological_sex(case_data)

    complaints = [
        element["id"]
        for element in case_data["presentingComplaints"]
        if element["state"] == "present"
    ]
    complaints += [
        element["id"]
        for element in case_data["otherFeatures"]
        if element["state"] == "present"
    ]
    complaints = set(complaints)

    conditions = []
    probabilities = []
    for condition in DATA["conditions"]:
        if condition["probability"][biological_sex] > 0.0:
            conditions.append(
                drop_all_but_keys(condition, ["id", "name", "expected_triage_level"])
            )
            probability = 0
            num_related_symptoms = 0
            for condition_id, symptom_id, _ in DATA["condition_symptom_probability"]:
                if condition_id == condition["id"]:
                    num_related_symptoms += 1
                    if symptom_id in complaints:
                        probability += 1
            probability /= num_related_symptoms
            probabilities.append(probability)

    conditions = sort_array_by_another_array(conditions, probabilities, reverse=True)

    conditions = conditions[:MAX_RETURNED_CONDITIONS]

    triage = conditions[0]["expected_triage_level"]

    conditions = [
        drop_all_but_keys(condition, ["id", "name"]) for condition in conditions
    ]

    return {"triage": triage, "conditions": conditions}


def health_check(request):
    """Emulates endpoint for health-checking an AI API"""
    ai_implementation = request["aiImplementation"]

    assert ai_implementation == "babylon_toy_ai"

    return {"status": "OK"}


def solve_case(request):
    case_data = request["caseData"]
    ai_implementation = request["aiImplementation"]

    assert ai_implementation == "babylon_toy_ai"

    return solve_case_by_symptom_intersection(case_data=case_data)
