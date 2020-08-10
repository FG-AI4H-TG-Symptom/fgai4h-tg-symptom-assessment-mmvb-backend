import random

import numpy
from common.definitions import BIOLOGICAL_SEXES, FIXTURES_DATA, TRIAGE_OPTIONS


def drop_all_but_keys(val, keys):
    """Filters dictionary keys and their values"""
    output = {}
    for key in keys:
        output[key] = val[key]
    return output


def extract_biological_sex(case_data):
    """Extracts biological sex information from profile in case data"""
    biological_sex = case_data["profileInformation"]["biologicalSex"]
    assert biological_sex in BIOLOGICAL_SEXES
    return biological_sex


# (https://stackoverflow.com/questions/6618515/
#  sorting-list-based-on-values-from-another-list)
def sort_array_by_another_array(values, map_for_ordering, reverse=False):
    """Sorts a list based on values from another list"""
    return [
        element
        for _, element in sorted(
            zip(map_for_ordering, values),
            key=lambda pair: pair[0],
            reverse=reverse,
        )
    ]


def get_modified_prior(condition, biological_sex, FIXTURES_DATA):

    prior = condition["prior"]
    sex_factor = next(
        item["weights"][biological_sex]
        for item in FIXTURES_DATA["condition_sex_weights"]
        if item["condition_id"] == condition["id"]
    )
    prior *= sex_factor

    return prior


def solve_case_random_conditions(case_data, randomisation_type):
    """
    Solves case given on `case_data` using the strategy given on
    `randomisation_type`
    """
    biological_sex = extract_biological_sex(case_data)

    conditions = []
    probabilities = []
    for condition in FIXTURES_DATA["conditions"]:

        modified_prior = get_modified_prior(
            condition, biological_sex, FIXTURES_DATA
        )

        if modified_prior > 0.0:
            conditions.append(
                drop_all_but_keys(condition, ["id", "short_name"])
            )
            probabilities.append(modified_prior)

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
