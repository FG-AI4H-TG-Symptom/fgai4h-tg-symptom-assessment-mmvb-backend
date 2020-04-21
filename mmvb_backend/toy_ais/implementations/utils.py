import json
import os
import random

import numpy

GENDERS = ["male", "female"]
EVIDENCE_STATES = ["present", "absent"]

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DATA = json.load(open(os.path.join(ROOT_DIR, "fixtures/data.json")))
SYMPTOM_ID_TO_SYMPTOMS = {
    symptom["id"]: symptom for symptom in FIXTURES_DATA["symptoms"]
}

OBSERVATION_PROBABILITY = 0.8
UNSURE_PROBABILITY = 0.1
MIN_AGE, MAX_AGE = 18, 80


def drop_all_but_keys(val, keys):
    output = {}
    for key in keys:
        output[key] = val[key]
    return output


def extract_biological_sex(case_data):
    biological_sex = case_data["profileInformation"]["biologicalSex"]
    assert biological_sex in GENDERS
    return biological_sex


# (https://stackoverflow.com/questions/6618515/
#  sorting-list-based-on-values-from-another-list)
def sort_array_by_another_array(values, map_for_ordering, reverse=False):
    return [
        element
        for _, element in sorted(
            zip(map_for_ordering, values),
            key=lambda pair: pair[0],
            reverse=reverse,
        )
    ]


def solve_case_random_conditions(case_data, randomisation_type):
    biological_sex = extract_biological_sex(case_data)

    conditions = []
    probabilities = []
    for condition in FIXTURES_DATA["conditions"]:
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
