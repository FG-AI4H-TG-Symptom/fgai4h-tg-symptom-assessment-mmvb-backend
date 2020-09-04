import random
from uuid import uuid4

from case_synthesizer.exceptions import SynthesisError
from cases.models import Case, CaseSet
from common.definitions import (
    BIOLOGICAL_SEXES,
    EVIDENCE_STATES,
    FACTOR_PROBABILITY,
    FIXTURES_DATA,
    MAX_AGE,
    MIN_AGE,
    OBSERVATION_PROBABILITY,
    PRESENT,
    UNKNOWN,
    UNSURE_PROBABILITY,
)
from common.utils import generate_id

WEIGHT_TO_PROBABILITY = {0: 0.0, 1: 30.0, 2: 60.0, 3: 90.0}
ID_TO_SYMPTOM = {
    symptom["id"]: symptom for symptom in FIXTURES_DATA["symptoms"]
}


def sample_attribute_values(symptom_weight):
    symptom = ID_TO_SYMPTOM[symptom_weight["symptom_id"]]
    attribute_values = []
    for attribute_weights in symptom_weight["attributes"]:
        attribute = next(
            attribute
            for attribute in symptom["attributes"]
            if attribute["id"] == attribute_weights["id"]
        )
        # TODO: Ignoring multiselection for now as not supported by schema
        value_id = random.choices(
            [value["id"] for value in attribute_weights["values"]],
            [value["weight"] for value in attribute_weights["values"]],
        )[0]
        value = next(
            value
            for value in attribute["value_set"]
            if value["id"] == value_id
        )
        attribute_values.append(
            {
                "id": attribute["id"],
                "name": attribute["term"],
                "standardOntologyUris": [attribute["sctid"]],
                "value": {
                    "id": value["id"],
                    "name": value["term"],
                    "standardOntologyUris": [value["sctid"]],
                },
            }
        )
    return attribute_values


def sample_symptoms(symptom_weights):
    """Samples symptoms and their states"""

    # Sample presenting symptom
    symptom_weight = random.choices(
        [item for item in symptom_weights],
        [WEIGHT_TO_PROBABILITY[item["weight"]] for item in symptom_weights],
    )[0]
    symptom = ID_TO_SYMPTOM[symptom_weight["symptom_id"]]
    attributes = sample_attribute_values(symptom_weight)
    presenting_symptom = {
        "id": symptom["id"],
        "name": symptom["term"],
        "standardOntologyUris": [symptom["sctid"]],
        "state": PRESENT,
        "attributes": attributes,
    }

    # Sample other symptoms
    symptom_states, symptom_attributes = {}, {}
    for symptom_weight in symptom_weights:
        symptom_id = symptom_weight["symptom_id"]
        if symptom_id == presenting_symptom["id"]:
            continue
        probability = WEIGHT_TO_PROBABILITY[symptom_weight["weight"]]
        state = random.choices(
            EVIDENCE_STATES, [probability, 1.0 - probability]
        )[0]
        symptom_states[symptom_id] = state
        symptom_attributes[symptom_id] = sample_attribute_values(
            symptom_weight
        )

    # Sample whether symptom is observed and known
    for symptom_id in symptom_states:
        if random.random() < OBSERVATION_PROBABILITY:
            symptom_states[symptom_id] = None
        elif random.random() < UNSURE_PROBABILITY:
            symptom_states[symptom_id] = UNKNOWN

    symptoms = []
    for symptom_id, state in symptom_states.items():
        if not state:
            continue
        symptom = ID_TO_SYMPTOM[symptom_id]
        attributes = symptom_attributes[symptom_id] if state == PRESENT else []
        symptoms.append(
            {
                "id": symptom["id"],
                "name": symptom["term"],
                "standardOntologyUris": [symptom["sctid"]],
                "state": state,
                "attributes": attributes,
            }
        )
    return presenting_symptom, symptoms


def generate_case_data():
    age = random.randint(MIN_AGE, MAX_AGE)
    biological_sex = random.choice(BIOLOGICAL_SEXES)

    sampled_factor_ids = [
        factor["id"]
        for factor in FIXTURES_DATA["factors"]
        if random.random() < FACTOR_PROBABILITY
    ]

    # Sample a condition based on priors and factors
    condition_priors = []
    for condition in FIXTURES_DATA["conditions"]:
        prior = condition["prior"]
        sex_factor = next(
            item["weights"][biological_sex]
            for item in FIXTURES_DATA["condition_sex_weights"]
            if item["condition_id"] == condition["id"]
        )
        prior *= sex_factor
        for factor in FIXTURES_DATA["condition_factor_weights"]:
            if factor["condition_id"] == condition["id"]:
                if factor["factor_id"] in sampled_factor_ids:
                    prior *= factor["weight"]
        condition_priors.append(prior)

    sampled_condition = random.choices(
        FIXTURES_DATA["conditions"], condition_priors
    )[0]

    # Sample symptoms based on weight of connection to sampled condition
    related_symptom_weights = [
        weight_info
        for weight_info in FIXTURES_DATA["condition_symptom_weights"]
        if weight_info["condition_id"] == sampled_condition["id"]
    ]
    presenting_symptom, symptoms = sample_symptoms(related_symptom_weights)

    if len(presenting_symptom) < 1:
        raise SynthesisError(
            "Something went wrong when sampling symptom states"
        )

    case_data = {
        "caseData": {
            "profileInformation": {
                "age": age,
                "biologicalSex": biological_sex,
            },
            "presentingComplaints": [presenting_symptom],
            "otherFeatures": symptoms,  # ADD FACTORS
        },
        "metaData": {
            "name": f"Synthesized case {str(uuid4())[:8]}",
            "caseCreator": "MMVB Berlin model case synthesizer",
        },
        "valuesToPredict": {
            "expectedTriageLevel": sampled_condition["triage"],
            "expectedCondition": {
                "id": sampled_condition["id"],
                "name": sampled_condition["term"],
                "standardOntologyUris": [sampled_condition["sctid"]],
            },
            "otherRelevantDifferentials": [],
            "impossibleConditions": [],
            "correctCondition": {
                "id": sampled_condition["id"],
                "name": sampled_condition["term"],
                "standardOntologyUris": [sampled_condition["sctid"]],
            },
        },
    }
    return case_data


def generate_cases(quantity):
    """
    Generates `quantity` of cases by sampling personal characteristics,
    conditions, symptoms and their states
    """
    cases = []

    for number in range(quantity):
        case_id = generate_id()
        case_data = generate_case_data()
        case = Case(id=case_id, data=case_data)
        cases.append(case)

    Case.objects.bulk_create(cases)

    return sorted(cases, key=lambda case: case.id)


def generate_casesets(quantity_of_casesets, cases_per_caseset, case_set_name):
    """
    Generates a `quantity_of_casesets` each containing an amount of
    `cases_per_caseset` cases
    """
    case_sets = []

    for quantity in range(quantity_of_casesets):
        case_id = generate_id()

        cases = generate_cases(cases_per_caseset)

        case_set = CaseSet(id=case_id, name=case_set_name)
        case_set.save()
        case_set.cases.add(*cases)
        case_sets.append(case_set)

    return sorted(case_sets, key=lambda case_set: case_set.id)
