import json
import os
import pandas as pd
import pathlib
import hashlib
from typing import Optional


def generate_id(
    concept_name: str, concept_id: str, scope: Optional[str] = None
) -> str:
    id_source = (
        concept_name.lower().replace(" ", "_")
        + ":"
        + concept_id
        + ("|" + scope if scope else "")
    )
    return hashlib.md5(id_source.encode("utf-8")).hexdigest()


# Source filenames
MODEL_SOURCE_DIR = os.path.join(
    pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent,
    "berlin-model-source"
)
MODEL_CSV = os.path.join(MODEL_SOURCE_DIR, "berlin-model.csv")
CONDITIONS_CSV = os.path.join(MODEL_SOURCE_DIR, "conditions.csv")
FINDINGS_CSV = os.path.join(MODEL_SOURCE_DIR, "clinical_findings.csv")
ATTRIBUTES_CSV = os.path.join(MODEL_SOURCE_DIR, "attributes-value_sets.csv")

# Output filename
OUTPUT_JSON_FILENAME = os.path.join(
    pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent,
    "mmvb_backend/common/fixtures/data.json"
)

# Row/column references
REFERENCE = "Reference"
ATTRIBUTE = "Attribute"

FINDING_TYPE = "Clinical finding type"
FINDING_SCTID = "Clinical finding SCTID"
FINDING_TERM = "Clinical finding term"
FINDING_SHORT_NAME = "Clinical finding short name"

ATTRIBUTE_SCTID = "Attribute SCTID or custom ID"
ATTRIBUTE_TERM = "Attribute term"
ATTRIBUTE_SHORT_NAME = "Attribute short name"
ATTRIBUTE_MULTISELECT = "Multiselect"

VALUE_SCTID = "Value SCTID or custom ID"
VALUE_TERM = "Value term"
VALUE_SHORT_NAME = "Value short name"

CONDITION_SCTID = "Condition SCTID"
CONDITION_TERM = "Condition term"
CONDITION_PRIOR = "Condition prior"
CONDITION_TRIAGE = "Condition triage"

COLUMNS = [
    REFERENCE,
    ATTRIBUTE,
    FINDING_TYPE,
    FINDING_SCTID,
    FINDING_SHORT_NAME,
    ATTRIBUTE_SCTID,
    ATTRIBUTE_SHORT_NAME,
    VALUE_SCTID,
    VALUE_SHORT_NAME,
]


SEX = "Sex"
FEMALE = "female"
MALE = "male"

SYMPTOM = "symptom"
FACTOR = "factor"
FINDING = "Clinical finding"

model_source = pd.read_csv(
    MODEL_CSV,
    dtype={FINDING_SCTID: str, ATTRIBUTE_SCTID: str, VALUE_SCTID: str}
)
conditions_source = pd.read_csv(CONDITIONS_CSV, dtype={CONDITION_SCTID: str})
findings_source = pd.read_csv(FINDINGS_CSV, dtype={FINDING_SCTID: str})
attributes_source = pd.read_csv(
    ATTRIBUTES_CSV,
    dtype={FINDING_SCTID: str, ATTRIBUTE_SCTID: str, VALUE_SCTID: str}
)

# Condition IDs
SCTID_TO_TERM = {
    row[CONDITION_SCTID]: row[CONDITION_TERM]
    for _, row in conditions_source.iterrows()
}
# Finding IDs
SCTID_TO_TERM.update(
    {
        row[FINDING_SCTID]: row[FINDING_TERM]
        for _, row in findings_source.iterrows()
    }
)
# Attribute IDs
SCTID_TO_TERM.update(
    {
        row[ATTRIBUTE_SCTID]: row[ATTRIBUTE_TERM]
        for _, row in attributes_source.dropna().iterrows()
    }
)
# Value IDs
SCTID_TO_TERM.update(
    {
        row[VALUE_SCTID]: row[VALUE_TERM]
        for _, row in attributes_source.iterrows()
    }
)

ATTRIBUTE_SCTID_TO_MULTISELECT = {
    row[ATTRIBUTE_SCTID]: row[ATTRIBUTE_MULTISELECT]
    for _, row in attributes_source.dropna().iterrows()
}

CONDITION_NAMES = [column for column in model_source.columns if column not in COLUMNS]

# Map symptom weights and fill empty cells
X_TO_WEIGHT = {"x": 1, "xx": 2, "xxx": 3}


def process_source_data(model_source):
    # Split source data

    condition_rows = [CONDITION_SCTID, CONDITION_PRIOR, CONDITION_TRIAGE]
    conditions_data = model_source[model_source[REFERENCE].isin(condition_rows)].copy()

    symptoms_data = model_source[model_source[FINDING_TYPE].fillna(method="ffill") == SYMPTOM].copy()
    symptoms_data[CONDITION_NAMES] = symptoms_data[CONDITION_NAMES].applymap(
        lambda x: X_TO_WEIGHT.get(x, 0)
    )
    symptoms_data.loc[
        symptoms_data[REFERENCE] == FINDING,
        [ATTRIBUTE_SCTID, ATTRIBUTE_SHORT_NAME, VALUE_SCTID, VALUE_SHORT_NAME]
    ] = "None"  # To prevent filling base symptom with attribute info
    symptoms_data.fillna(method="ffill", inplace=True)

    factors_data = model_source[model_source[FINDING_TYPE].fillna(method="ffill") == FACTOR].copy()

    sex_data = model_source[model_source[REFERENCE].fillna(method="ffill") == SEX].copy()

    return conditions_data, symptoms_data, factors_data, sex_data


def get_conditions(conditions_data):
    # Compile list of conditions
    conditions = []
    for condition_name in CONDITION_NAMES:
        sctid = conditions_data[conditions_data[REFERENCE] == CONDITION_SCTID][condition_name].iloc[0]
        prior = conditions_data[conditions_data[REFERENCE] == CONDITION_PRIOR][condition_name].iloc[0]
        triage = conditions_data[conditions_data[REFERENCE] == CONDITION_TRIAGE][condition_name].iloc[0]
        condition = {
            "id": generate_id("Condition", sctid),
            "short_name": condition_name,
            "sctid": sctid,
            "term": SCTID_TO_TERM[sctid],
            "prior": X_TO_WEIGHT.get(prior, 0),
            "triage": triage,
        }
        conditions.append(condition)
    return conditions


def get_symptoms(symptoms_data):
    # Compile list of symptoms
    symptoms = []
    for symptom_sctid, symptom_data in symptoms_data.groupby(FINDING_SCTID):
        attributes = []
        attribute_data = symptom_data[symptom_data[ATTRIBUTE_SCTID] != "None"]
        symptom_id = generate_id("Clinical finding", symptom_sctid)
        for _, attribute_group in attribute_data.groupby(ATTRIBUTE_SCTID):
            attribute_sctid = attribute_group[ATTRIBUTE_SCTID].iloc[0]
            attribute_id = generate_id("Attribute", attribute_sctid, symptom_id)
            attribute = {
                "id": attribute_id,
                "short_name": attribute_group[ATTRIBUTE_SHORT_NAME].iloc[0],
                "sctid": attribute_sctid,
                "term": SCTID_TO_TERM[attribute_sctid],
                "multiselect": ATTRIBUTE_SCTID_TO_MULTISELECT[attribute_sctid],
                "value_set": [
                    {
                        "id": generate_id("Value", value_data[VALUE_SCTID], attribute_id),
                        "short_name": value_data[VALUE_SHORT_NAME],
                        "sctid": value_data[VALUE_SCTID],
                        "term": SCTID_TO_TERM[value_data[VALUE_SCTID]],
                    }
                    for _, value_data in attribute_group.iterrows()
                ],
            }
            attributes.append(attribute)

        symptom = {
            "id": symptom_id,
            "short_name": symptom_data[FINDING_SHORT_NAME].iloc[0],
            "sctid": symptom_sctid,
            "term": SCTID_TO_TERM[symptom_sctid],
            "attributes": attributes
        }
        symptoms.append(symptom)
    return symptoms


def get_factors(factors_data):
    # Compile list of factors
    factors = []
    for factor_sctid, factor_data in factors_data.groupby(FINDING_SCTID):
        factor = {
            "id": generate_id("Clinical finding", factor_sctid),
            "short_name": factor_data[FINDING_SHORT_NAME].iloc[0],
            "sctid": factor_sctid,
            "term": SCTID_TO_TERM[factor_sctid],
            "attributes": []
        }
        factors.append(factor)
    return factors


def get_condition_symptom_weights(symptoms_data, conditions):
    # Compile list of disease to symptom weights
    condition_symptom_weights = []
    for symptom_sctid, symptom_data in symptoms_data.groupby(FINDING_SCTID):
        for condition_name in CONDITION_NAMES:
            condition_id = next(
                condition["id"] for condition in conditions
                if condition["short_name"] == condition_name
            )
            symptom_id = generate_id("Clinical finding", symptom_sctid)
            attribute_weights = []
            attribute_data = symptom_data[symptom_data[ATTRIBUTE_SCTID] != "None"]
            for _, attribute_group in attribute_data.groupby(ATTRIBUTE_SCTID):
                attribute_sctid = attribute_group[ATTRIBUTE_SCTID].iloc[0]
                attribute_id = generate_id("Attribute", attribute_sctid, symptom_id)
                attribute_weight = {
                    "id": attribute_id,
                    "values": [
                        {
                            "id": generate_id("Value", value_data[VALUE_SCTID], attribute_id),
                            "weight": int(value_data[condition_name]),
                        }
                        for _, value_data in attribute_group.iterrows()
                    ]
                }
                attribute_weights.append(attribute_weight)
            condition_symptom_weight = {
                "condition_id": condition_id,
                "symptom_id": symptom_id,
                "weight": int(symptom_data[symptom_data[ATTRIBUTE_SCTID] == "None"][condition_name].iloc[0]),
                "attributes": attribute_weights,
            }
            condition_symptom_weights.append(condition_symptom_weight)
    return condition_symptom_weights


def get_condition_factor_weights(factors_data, conditions):
    # Compile list of factor to disease weights
    condition_factor_weights = []
    for factor_sctid, factor_data in factors_data.groupby(FINDING_SCTID):

        for condition_name in CONDITION_NAMES:
            condition_id = next(
                condition["id"] for condition in conditions
                if condition["short_name"] == condition_name
            )
            condition_factor_weight = {
                "condition_id": condition_id,
                "factor_id": generate_id("Clinical finding", factor_sctid),
                "weight": float(factor_data[condition_name].iloc[0]),
                "attributes": []
            }
            condition_factor_weights.append(condition_factor_weight)
    return condition_factor_weights


def get_condition_sex_weights(sex_data, conditions):
    # Compile list of sex weights
    condition_sex_weights = []
    for condition_name in CONDITION_NAMES:
        condition_id = next(
            condition["id"] for condition in conditions
            if condition["short_name"] == condition_name
        )
        condition_sex_weights.append(
            {
                "condition_id": condition_id,
                "weights": {
                    "female": float(sex_data[sex_data[ATTRIBUTE] == FEMALE][condition_name].iloc[0]),
                    "male": float(sex_data[sex_data[ATTRIBUTE] == MALE][condition_name].iloc[0]),
                }
            }
        )
    return condition_sex_weights


def parse_berlin_model():
    conditions_data, symptoms_data, factors_data, sex_data = process_source_data(model_source)

    conditions = get_conditions(conditions_data)
    symptoms = get_symptoms(symptoms_data)
    factors = get_factors(factors_data)
    condition_symptom_weights = get_condition_symptom_weights(symptoms_data, conditions)
    condition_factor_weights = get_condition_factor_weights(factors_data, conditions)
    condition_sex_weights = get_condition_sex_weights(sex_data, conditions)

    model_data = {
        "conditions": conditions,
        "symptoms": symptoms,
        "factors": factors,
        "condition_symptom_weights": condition_symptom_weights,
        "condition_factor_weights": condition_factor_weights,
        "condition_sex_weights": condition_sex_weights,
    }

    json.dump(model_data, open(OUTPUT_JSON_FILENAME, "w"), indent=2)


if __name__ == "__main__":
    parse_berlin_model()
