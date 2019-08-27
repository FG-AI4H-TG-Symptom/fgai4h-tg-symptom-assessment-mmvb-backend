import json
import os
import random
import sys
import time
from multiprocessing import Process

import numpy as np
from deepdiff import DeepDiff

from config import CONFIG_DEFAULT_HOST
from evaluator import api

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_CASES = [
    {
        "caseData": {
            "caseId": "case_mmvb_0_0_1_a_85822412",
            "metaData": {"description": "a synthetic case for the MMVB"},
            "otherFeatures": [],
            "presentingComplaints": [
                {
                    "id": "94b2b09c9194b316738dfc56b526e124",
                    "name": "heartburn",
                    "state": "present",
                }
            ],
            "profileInformation": {"age": 23, "biologicalSex": "male"},
        },
        "valuesToPredict": {
            "condition": {"id": "ed9e333b5cf04cb91068bbcde643076e", "name": "GERD"},
            "expectedTriageLevel": "PC",
        },
    },
    {
        "caseData": {
            "caseId": "case_mmvb_0_0_1_a_73197857",
            "metaData": {"description": "a synthetic case for the MMVB"},
            "otherFeatures": [
                {
                    "id": "c643bff833aaa9a47e3421a8c8f35445",
                    "name": "Vomiting",
                    "state": "absent",
                }
            ],
            "presentingComplaints": [
                {
                    "id": "1e400ff9b77134121117183e3fc9b7a2",
                    "name": "Abdo Pain Cramping Central 2 days",
                    "state": "present",
                }
            ],
            "profileInformation": {"age": 22, "biologicalSex": "female"},
        },
        "valuesToPredict": {
            "condition": {
                "id": "42e009a4e3d8c8a17a29b4c57311e9cf",
                "name": "IBD (first presentation non flare)",
            },
            "expectedTriageLevel": "PC",
        },
    },
]


AI_RESULTS = [
    {
        "conditions": [
            {
                "id": "42e009a4e3d8c8a17a29b4c57311e9cf",
                "name": "IBD (first presentation non flare)",
            },
            {"id": "379771d589cd397c770bb6915c3c17a6", "name": "acute pyelonephritis"},
            {"id": "85473ef69bd60889a208bc1a65dc0cb8", "name": "simple UTI"},
        ],
        "triage": "PC",
    },
    {
        "conditions": [
            {
                "id": "42e009a4e3d8c8a17a29b4c57311e9cf",
                "name": "IBD (first presentation non flare)",
            },
            {"id": "379771d589cd397c770bb6915c3c17a6", "name": "acute pyelonephritis"},
            {"id": "85473ef69bd60889a208bc1a65dc0cb8", "name": "simple UTI"},
        ],
        "triage": "PC",
    },
]


def start_case_generator_server():
    sys.path.append(os.path.join(ROOT_DIR, "case_generator"))
    import case_generator.app

    random.seed(42)
    np.random.seed(42)
    cg_app = case_generator.app.create_app()
    cg_app.run(port=5001, host=CONFIG_DEFAULT_HOST)


def start_toy_ai_server():
    sys.path.append(os.path.join(ROOT_DIR, "toy_ai"))
    import toy_ai.app

    random.seed(42)
    np.random.seed(42)
    ai_app = toy_ai.app.create_app()
    ai_app.run(port=5002, host=CONFIG_DEFAULT_HOST)


def test_generate_case_set():
    p = Process(target=start_case_generator_server)
    p.start()
    try:
        time.sleep(1)
        case_info = {"numCases": 2}
        res = api.generate_case_set(case_info)
        with open(
            os.path.join(
                ROOT_DIR, "evaluator", "data", res["case_set_id"], "cases.json"
            ),
            "r",
        ) as f:
            res = json.load(f)
        assert DeepDiff(res, TEST_CASES) == dict()
        p.terminate()
    except AssertionError:
        p.terminate()
        raise


def test_run_case_set_against_ai():
    p = Process(target=start_toy_ai_server)
    p.start()
    request = {
        "caseSetId": "1_1",
        "aiLocationPath": "http://0.0.0.0:5002/toy-ai/v1/solve-case",
        "aiImplementation": "toy_ai_deterministic_by_symptom_intersection",
        "runName": "toy_ai_deterministic_by_symptom_intersection",
    }

    random.seed(42)
    np.random.seed(42)
    try:
        time.sleep(1)
        res = api.run_case_set_against_ai(request)
        assert DeepDiff(res["results"], AI_RESULTS) == dict()
        p.terminate()
    except AssertionError:
        p.terminate()
        raise
