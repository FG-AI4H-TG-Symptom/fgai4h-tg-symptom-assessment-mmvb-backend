import random

import numpy as np
from deepdiff import DeepDiff

from case_generator import api


def test_generate_case():
    np.random.seed(42)
    random.seed(42)
    res = api.generate_case()

    comp = {
        "caseData": {
            "caseId": "case_mmvb_0_0_1_a_85822412",
            "metaData": {"description": "a synthetic case for the MMVB"},
            "profileInformation": {"biologicalSex": "male", "age": 25},
            "presentingComplaints": [
                {
                    "id": "94b2b09c9194b316738dfc56b526e124",
                    "name": "heartburn",
                    "state": "present",
                }
            ],
            "otherFeatures": [],
        },
        "valuesToPredict": {
            "expectedTriageLevel": "PC",
            "condition": {"id": "ed9e333b5cf04cb91068bbcde643076e", "name": "GERD"},
        },
    }

    assert DeepDiff(res, comp) == {}
