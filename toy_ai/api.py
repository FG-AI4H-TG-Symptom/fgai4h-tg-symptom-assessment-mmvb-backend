# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import json
import os
import random

import numpy

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_RETURNED_CONDITIONS = 3


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


def solve_case_random_conditions(case_data, randomisation_type):
    biological_sex = extract_biological_sex(case_data)

    conditions = []
    probabilities = []
    for condition in DATA["conditions"]:
        if condition["probability"][biological_sex] > 0.0:
            conditions.append(drop_all_but_keys(condition, ["id", "name"]))
            probabilities.append(condition["probability"][biological_sex])

    num_of_conditions = random.randint(0, 5)

    if randomisation_type == "uniform":
        prob = None
    elif randomisation_type == "probability_weighted":
        prob = [element / sum(probabilities) for element in probabilities]
    else:
        raise ValueError(
            "AI Module: Randomisation strategy cannot be "
            f"handled: {randomisation_type}"
        )

    conditions = numpy.random.choice(
        conditions, num_of_conditions, replace=False, p=prob
    )
    conditions = [element for element in conditions]

    triage = random.choice(["SC", "PC", "EC", "UNCERTAIN"])

    return {"triage": triage, "conditions": conditions}


def solve_case_deterministic_most_likely_conditions(case_data):
    biological_sex = extract_biological_sex(case_data)

    conditions = []
    probabilities = []
    for condition in DATA["conditions"]:
        if condition["probability"][biological_sex] > 0.0:
            conditions.append(drop_all_but_keys(condition, ["id", "name"]))
            probabilities.append(condition["probability"][biological_sex])

    conditions = sort_array_by_another_array(conditions, probabilities)

    conditions = conditions[:MAX_RETURNED_CONDITIONS]

    triage = "PC"

    return {"triage": triage, "conditions": conditions}


def solve_case_by_symptom_intersection(case_data):
    biological_sex = extract_biological_sex(case_data)

    complaints = [
        element["id"]
        for element in case_data["presentingComplaints"]
        if element["state"] == "true"
    ]
    complaints += [
        element["id"]
        for element in case_data["otherComplaints"]
        if element["state"] == "true"
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


def solve_case(request):
    case_data = request["caseData"]
    ai_implementation = request["aiImplementation"]

    if ai_implementation == "toy_ai_random_uniform":
        return solve_case_random_conditions(
            case_data=case_data, randomisation_type="uniform"
        )
    elif ai_implementation == "toy_ai_random_probability_weighted":
        return solve_case_random_conditions(
            case_data=case_data, randomisation_type="probability_weighted"
        )
    elif ai_implementation == "toy_ai_deterministic_most_likely_conditions":
        return solve_case_deterministic_most_likely_conditions(case_data=case_data)
    elif ai_implementation == "toy_ai_deterministic_by_symptom_intersection":
        return solve_case_by_symptom_intersection(case_data=case_data)
    else:
        raise ValueError(
            "AI Module: Selected AI implementation cannot be "
            f"handled: {ai_implementation}"
        )
