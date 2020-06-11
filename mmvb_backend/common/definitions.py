import json
import os
from enum import Enum


class HealthCheckStatus(Enum):
    """Definitions of expected health check status"""

    OK = "ok"
    BAD_RESPONSE = "bad response"
    TIMEOUT = "timeout"


# Common definitions to be shared with and used by other applications
BIOLOGICAL_SEXES = ["male", "female"]
PRESENT = "present"
ABSENT = "absent"
UNKNOWN = "unsure"
EVIDENCE_STATES = [PRESENT, ABSENT]
EXPECTED_TRIAGE_OPTIONS = ["SC", "PC", "EC"]
TRIAGE_OPTIONS = EXPECTED_TRIAGE_OPTIONS + ["UNCERTAIN"]

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DATA = json.load(open(os.path.join(ROOT_DIR, "fixtures/data.json")))
SYMPTOM_ID_TO_SYMPTOMS = {
    symptom["id"]: symptom for symptom in FIXTURES_DATA["symptoms"]
}

OBSERVATION_PROBABILITY = 0.8
UNSURE_PROBABILITY = 0.1
MIN_AGE, MAX_AGE = 18, 80
SOFT_FAIL_TRIAGE_SIMILARITY = 0.2
