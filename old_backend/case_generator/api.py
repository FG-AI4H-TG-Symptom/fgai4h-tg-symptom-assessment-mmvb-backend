# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import json
import os
import random

GENDERS = ["male", "female"]
EVIDENCE_STATES = ["present", "absent"]

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT_DIR, "data/data.json")))
SYMPTOM_ID_TO_SYMPTOMS = {
    symptom["id"]: symptom for symptom in DATA["symptoms"]
}

OBSERVATION_PROBABILITY = 0.8
UNSURE_PROBABILITY = 0.1
MIN_AGE, MAX_AGE = 18, 80


def sample_symptoms(symptom_probabilities):
    # Sample latent state
    symptom_states = {}
    for symptom, probability in symptom_probabilities.items():
        state = random.choices(
            EVIDENCE_STATES, [probability, 1.0 - probability]
        )[0]
        symptom_states[symptom] = state

    # Sample whether state is known
    for symptom in symptom_states:
        if random.random() < OBSERVATION_PROBABILITY:
            symptom_states[symptom] = None

    # Sample whether user answers "I don't know"
    for symptom, state in symptom_states.items():
        if not state:
            continue
        if random.random() < UNSURE_PROBABILITY:
            symptom_states[symptom] = "unsure"

    # Ensure at least one present symptom
    if "present" not in symptom_states.values():
        symptom = max(symptom_probabilities, key=symptom_probabilities.get)
        symptom_states[symptom] = "present"

    return {
        symptom: state for symptom, state in symptom_states.items() if state
    }


def combine_symptom_and_state(symptom, state_value):
    # Combining two dictionaries together:
    return {**symptom, **{"state": state_value}}


def generate_case():
    # TODO: Better case_id generation without hash collision possibility
    case_id = "case_mmvb_0_0_1_a_" + str(random.randint(0, 1e8))
    age = random.randint(MIN_AGE, MAX_AGE)
    biological_sex = random.choice(GENDERS)
    meta_data = {"description": "a synthetic case for the MMVB"}

    # Sample from conditions based on their probabilities
    condition_probabilities = [
        condition_info["probability"][biological_sex]
        for condition_info in DATA["conditions"]
    ]

    # TODO: Add option to draw cases uniformly from available conditions
    sampled_condition = random.choices(
        DATA["conditions"], condition_probabilities
    )[0]

    symptom_probabilities = {
        symptom_id: probability
        for condition_id, symptom_id, probability in DATA[
            "condition_symptom_probability"
        ]
        if condition_id == sampled_condition["id"]
    }

    assert len(symptom_probabilities) > 0

    symptom_states = sample_symptoms(symptom_probabilities)

    assert len(symptom_states) > 0

    symptoms = [
        combine_symptom_and_state(symptom, symptom_states.get(symptom["id"]))
        for symptom in DATA["symptoms"]
        if symptom["id"] in symptom_states
    ]

    # Split a present symptom as presenting symptom
    presenting_symptom = symptoms.pop(
        [
            index
            for index, symptom in enumerate(symptoms)
            if symptom["state"] == "present"
        ][0]
    )

    output = {
        "caseData": {
            "caseId": case_id,
            "metaData": meta_data,
            "profileInformation": {
                "biologicalSex": biological_sex,
                "age": age,
            },
            "presentingComplaints": [presenting_symptom],
            "otherFeatures": symptoms,
        },
        "valuesToPredict": {
            "expectedTriageLevel": sampled_condition["expected_triage_level"],
            "condition": {
                "id": sampled_condition["id"],
                "name": sampled_condition["name"],
            },
        },
    }

    return output
