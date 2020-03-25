from enum import IntEnum


class ProcessSignal(IntEnum):
    HEALTH_CHECK = 1
    SOLVE_CASE = 2
    SENTINEL = 3
    TERMINATE = -1
