# This is a component of the MMVB for the "Symptom assessment" sub-group
# (of the the International Telecommunication Union focus group
# "Artificial Intelligence for Health".
# For copyright and licence, see the parent directory.

import glob
import hashlib
import json
import os
import time

import requests

SERVER_HOST_FOR_CASE_GENERATION = "http://0.0.0.0:5001"

TIMEOUT = 0.5  # in seconds

FILE_DIR = os.path.dirname((os.path.abspath(__file__)))


def create_dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_unique_id():
    return str(time.time()).replace(".", "_")


def parse_validate_caseSetId(caseSetId):
    case_set_id = str(caseSetId)
    for char in case_set_id:
        assert char in [str(x) for x in range(10)] or char == "_"
    return case_set_id


def md5(value):
    return hashlib.md5(value.encode()).hexdigest()


def generate_case_set(request):
    num_cases = int(request["numCases"])
    # TODO: Gracefully fail for >1000 cases
    assert num_cases > 0 and num_cases <= 1000

    cases = []

    for case_id in range(num_cases):
        request = requests.get(
            SERVER_HOST_FOR_CASE_GENERATION + "/case-generator/v1/generate-case"
        )
        assert request.status_code == 200
        cases.append(request.json())

    case_set_id = get_unique_id()
    path = os.path.join(FILE_DIR, "data", case_set_id)

    create_dirs(path)

    json.dump(cases, open(os.path.join(path, "cases.json"), "w"), indent=2)

    return {"case_set_id": case_set_id}


def list_case_sets():
    path = os.path.join(FILE_DIR, "data/")

    return {
        "existing_case_sets": [
            element.replace(path, "") for element in glob.glob(path + "*")
        ]
    }


def extract_case_set(caseSetId):
    case_set_id = parse_validate_caseSetId(caseSetId)

    return {
        "cases": json.load(
            open(os.path.join(FILE_DIR, "data", case_set_id, "cases.json"))
        )
    }


def run_case_set_against_ai(request):
    case_set_id = parse_validate_caseSetId(request["caseSetId"])
    ai_location_path = request["aiLocationPath"]
    ai_implementation = request["aiImplementation"]
    run_name = request["runName"]

    run_hash = get_unique_id()

    path = os.path.join(FILE_DIR, "data", case_set_id, run_hash)

    cases = json.load(open(os.path.join(FILE_DIR, "data", case_set_id, "cases.json")))

    results = []

    for case in cases:
        try:
            request = requests.post(
                ai_location_path,
                json={
                    "aiImplementation": ai_implementation,
                    "caseData": case["caseData"],
                },
                timeout=TIMEOUT,
            )

            assert request.status_code == 200
            response = request.json()
        except AssertionError:
            response = None

        results.append(response)

    create_dirs(path)

    json.dump(
        {
            "ai_location_path": ai_location_path,
            "ai_implementation": ai_implementation,
            "run_name": run_name,
        },
        open(os.path.join(path, "meta.json"), "w"),
        indent=2,
    )

    json.dump(results, open(os.path.join(path, "results.json"), "w"), indent=2)

    return {"runId": run_hash, "results": results}
