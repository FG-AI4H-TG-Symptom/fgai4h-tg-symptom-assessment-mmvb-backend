# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

"""
Converting the spreadsheet (downloaded as a CSV)
https://docs.google.com/spreadsheets/d/111D40yoJqvvHZEYI8RNSnemGf0abC9hQjQ7crFzNrdk/edit?ts=5d28438b#gid=575520860
into a JSON file.
"""

import csv
import hashlib
import json

GENDERS = ("male", "female")

LIKELIHOOD_MAP = {"x": 0.3, "xx": 0.6, "xxx": 0.9}


def extract_condition_probability(value):

    if value == "x, only females":
        return {"male": 0.0, "female": LIKELIHOOD_MAP["x"]}
    elif value in LIKELIHOOD_MAP.keys():
        return {gender: LIKELIHOOD_MAP[value] for gender in GENDERS}
    else:
        raise ValueError(
            "Data loader: Condition likeliness cannot be handled: " f"{value}"
        )


def map_likelihood(value):
    if value == "":
        return None
    elif value in LIKELIHOOD_MAP.keys():
        return LIKELIHOOD_MAP[value]
    else:
        raise ValueError(
            "Data loader: Condition likeliness cannot be handled: " f"{value}"
        )


def map_expected_triage_level(value):
    if value in ["SC", "PC", "EC"]:
        return value
    elif value == "SC/PC":
        return "SC"
    else:
        raise ValueError(
            "Data loader: Expected triage level cannot be " f"handled: {value}"
        )


def md5(value):
    return hashlib.md5(value.encode()).hexdigest()


conditions = set()
symptoms = set()
column_id_to_condition_map = {}
condition_probability = {}
condition_to_expected_triage_level = {}
condition_symptom_probability = []


with open(
    "symptom condition mapping - Matrix official.csv", newline=""
) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=",", quotechar='"')
    for row_id, row in enumerate(csvreader):
        if row_id == 0:
            for column_id, column_value in enumerate(row):
                if column_id > 1:
                    assert column_value not in conditions
                    conditions.add(column_value)
                    column_id_to_condition_map[column_id] = column_value
        elif row_id == 2:
            for column_id, column_value in enumerate(row):
                if column_id > 1:
                    condition_name = column_id_to_condition_map[column_id]
                    condition_probability[
                        condition_name
                    ] = extract_condition_probability(column_value)
        elif row_id > 2:
            if row[0] == "Expected triage level":
                for column_id, column_value in enumerate(row):
                    if column_id > 1:
                        condition_name = column_id_to_condition_map[column_id]
                        condition_to_expected_triage_level[
                            condition_name
                        ] = map_expected_triage_level(column_value)
            else:
                symptom_name = row[0]
                assert symptom_name not in symptoms
                symptoms.add(symptom_name)
                for column_id, column_value in enumerate(row):
                    if column_id > 1:
                        assert column_value in ["", "x", "xx", "xxx"]

                        pair_likelihood = map_likelihood(column_value)

                        if pair_likelihood is not None:
                            condition_symptom_probability.append(
                                [
                                    md5(column_id_to_condition_map[column_id]),
                                    md5(symptom_name),
                                    pair_likelihood,
                                ]
                            )

data_symptoms = [{"id": md5(symptom), "name": symptom} for symptom in symptoms]

data_conditions = [
    {
        "id": md5(condition),
        "name": condition,
        "probability": condition_probability[condition],
        "expected_triage_level": condition_to_expected_triage_level[condition],
    }
    for condition in conditions
]

data = {
    "symptoms": data_symptoms,
    "conditions": data_conditions,
    "condition_symptom_probability": condition_symptom_probability,
}

json.dump(data, open("data.json", "w"), indent=2, sort_keys=True)
