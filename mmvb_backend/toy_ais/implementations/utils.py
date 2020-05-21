import random

import numpy
from common.definitions import BIOLOGICAL_SEXES, FIXTURES_DATA, TRIAGE_OPTIONS


def drop_all_but_keys(val, keys):
    output = {}
    for key in keys:
        output[key] = val[key]
    return output


def extract_biological_sex(case_data):
    biological_sex = case_data["profile_information"]["biological_sex"]
    assert biological_sex in BIOLOGICAL_SEXES
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

    triage = random.choice(TRIAGE_OPTIONS)

    return {"triage": triage, "conditions": conditions}
