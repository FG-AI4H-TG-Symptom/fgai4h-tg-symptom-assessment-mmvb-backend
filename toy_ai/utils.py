import time


class TypeOneSimulatedError(Exception):
    pass


class TypeTwoSimulatedError(Exception):
    pass


def solve_case_error_type_one(case_data, *args):
    raise TypeOneSimulatedError(
        f'This is a Type One Simulated Error for case with id {case_data["caseId"]}')


def solve_case_error_type_two(case_data, *args):
    raise TypeTwoSimulatedError(
        f'This is a Type Two Simulated Error for case with id {case_data["caseId"]}')


def solve_case_soft_timeout(case_data, randomisation_type, callback=None):
    time.sleep(7)
    if callback:
        return callback(case_data, randomisation_type)
    return {}


def solve_case_hard_timeout(case_data, randomisation_type, callback=None):
    time.sleep(15)
    if callback:
        return callback(case_data, randomisation_type)
    return {}
