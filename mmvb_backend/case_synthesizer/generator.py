import random

from case_synthesizer.exceptions import SynthesisError
from cases.models import Case, CaseSet
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
        meta_data = {
            "description": f"Synthetic London-model case ({number+1}/{quantity})"
        }

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
            raise SynthesisError(
                "Something went wrong when generating symptom probabilities"
            )

        symptom_states = sample_symptoms(symptom_probabilities)

        if len(symptom_states) <= 0:
            raise SynthesisError(
                "Something went wrong when sampling symptom states"
            )

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


def generate_casesets(quantity_of_casesets, cases_per_caseset):
    case_sets = []

    for quantity in range(quantity_of_casesets):
        case_id = generate_id()
        name = case_id.hex
        cases = generate_cases(cases_per_caseset)

        case_set = CaseSet(id=case_id, name=name)
        case_set.save()
        case_set.cases.add(*cases)
        case_sets.append(case_set)

    return sorted(case_sets, key=lambda case_set: case_set.id)
