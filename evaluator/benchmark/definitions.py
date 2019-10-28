from enum import IntEnum

# TODO: Make configurable
MAX_NUM_ATTEMPTS = 10
MAX_WAIT_BETWEEN_RETRIES = 3
SOLVE_CASE_SOFT_TIMEOUT = 5
SOLVE_CASE_HARD_TIMEOUT = 10


class ManagerStatuses(IntEnum):
    IDLE = 0
    RUNNING = 1


class CaseStatuses(IntEnum):
    RUNNING = 0
    OK = 1
    ERROR = -1
