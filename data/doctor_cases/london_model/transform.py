import csv
import json

model_data = json.load(open("../../data.json"))
concept_names_to_ids = {}
for condition in model_data["conditions"]:
    concept_names_to_ids[condition["name"]] = condition["id"]
for condition in model_data["symptoms"]:
    concept_names_to_ids[condition["name"]] = condition["id"]

STATE_MAPPING = {"present": "true", "absent": "false", "unknown": "unsure"}

TRIAGE_MAPPING = {"self_care": "SC", "primary_care": "PC", "emergency": "EC"}


def create_concept(concept_name):
    return {"name": concept_name, "id": concept_names_to_ids[concept_name]}


def create_concept_and_state(concept_name, concept_state):
    assert concept_state in ["true", "false", "unsure"]
    return dict(state=concept_state, **create_concept(concept_name))


def record_last_case(current_case, cases, other_features):
    if current_case is not None:
        current_case["caseData"]["otherFeatures"] = other_features
        cases.append(current_case)


CASES = []

with open("CollectingCasesLondonModel.csv") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=",", quotechar='"')

    current_case = None
    other_features = None

    for row_index, row in enumerate(csvreader):
        row = [cell.strip() for cell in row]

        if row_index > 0 and row[0] != "":
            # Function `record_last_case(...)` needs to be called one more time below.
            record_last_case(current_case, CASES, other_features)

            current_case = {}
            other_features = []
            case_index = len(CASES)

            age = int(row[3])
            assert age >= 18 and age <= 99

            sex = row[4]
            assert sex in ["male", "female"]

            presenting_complaint_concept_and_state = create_concept_and_state(
                row[5], "true"
            )

            # Note: the `otherFeatures` are recorded below in a separate "if".

            expected_triage = TRIAGE_MAPPING[row[8]]

            expected_condition = create_concept(row[9])

            current_case["caseData"] = {
                "caseId": "human_doctor_case_london_model_spreadsheet111D40_case_"
                + str(case_index),
                "profileInformation": {"age": age, "biologicalSex": sex},
                "presentingComplaints": [presenting_complaint_concept_and_state],
                "metaData": {
                    "description": "A case created by a human doctor (the London 2019 model cases)",  # noqa: E501
                    "case_creator": row[1],
                    "spreadsheet_case_id": row[2],
                },
            }
            current_case["valuesToPredict"] = {
                "expectedTriageLevel": expected_triage,
                "condition": expected_condition,
            }

        if row[6] != "" and current_case is not None:
            other_features += [create_concept_and_state(row[6], STATE_MAPPING[row[7]])]

record_last_case(current_case, CASES, other_features)

CASES = [
    case
    for case in CASES
    if case["caseData"]["metaData"]["spreadsheet_case_id"][:3] != "CC_"
]

json.dump(CASES, open("cases.json", "w"), indent=2)
