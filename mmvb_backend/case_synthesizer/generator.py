import random

from cases.models import Case
from common.definitions import (
    BIOLOGICAL_SEXES,
    EVIDENCE_STATES,
    FIXTURES_DATA,
    MAX_AGE,
    MIN_AGE,
    OBSERVATION_PROBABILITY,
    PRESENT,
    UNKNOWN,
    UNSURE_PROBABILITY,
)
from common.utils import generate_id


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
            symptom_states[symptom] = UNKNOWN

    # Ensure at least one present symptom
    if PRESENT not in symptom_states.values():
        symptom = max(symptom_probabilities, key=symptom_probabilities.get)
        symptom_states[symptom] = PRESENT

    return {
        symptom: state for symptom, state in symptom_states.items() if state
    }


def combine_symptom_and_state(symptom, state_value):
    # Combining two dictionaries together:
    return {**symptom, **{"state": state_value}}


def generate_cases(quantity):
    cases = []

    for number in range(quantity):
        case_id = generate_id()
        age = random.randint(MIN_AGE, MAX_AGE)
        biological_sex = random.choice(BIOLOGICAL_SEXES)
        meta_data = {"description": "a synthetic case for the MMVB"}

        # Sample from conditions based on their probabilities
        condition_probabilities = [
            condition_info["probability"][biological_sex]
            for condition_info in FIXTURES_DATA["conditions"]
        ]

        sampled_condition = random.choices(
            FIXTURES_DATA["conditions"], condition_probabilities
        )[0]

        symptom_probabilities = {
            symptom_id: probability
            for condition_id, symptom_id, probability in FIXTURES_DATA[
                "condition_symptom_probability"
            ]
            if condition_id == sampled_condition["id"]
        }

        if len(symptom_probabilities) <= 0:
            raise EnvironmentError

        symptom_states = sample_symptoms(symptom_probabilities)

        if len(symptom_states) <= 0:
            raise EnvironmentError

        symptoms = [
            combine_symptom_and_state(
                symptom, symptom_states.get(symptom["id"])
            )
            for symptom in FIXTURES_DATA["symptoms"]
            if symptom["id"] in symptom_states
        ]

        # Split a present symptom as presenting symptom
        presenting_symptom = symptoms.pop(
            [
                index
                for index, symptom in enumerate(symptoms)
                if symptom["state"] == PRESENT
            ][0]
        )

        case = Case(
            id=case_id,
            data={
                "case_data": {
                    "meta_data": meta_data,
                    "profile_information": {
                        "biological_sex": biological_sex,
                        "age": age,
                    },
                    "presenting_complaints": [presenting_symptom],
                    "other_features": symptoms,
                },
                "values_to_predict": {
                    "expected_triage_level": (
                        sampled_condition["expected_triage_level"]
                    ),
                    "condition": {
                        "id": sampled_condition["id"],
                        "name": sampled_condition["name"],
                    },
                },
            },
        )
        cases.append(case)

    Case.objects.bulk_create(cases)

    return sorted(cases, key=lambda case: case.id)
