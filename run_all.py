import os
import sys
from multiprocessing import Process

from config import CONFIG_DEFAULT_HOST

ORIGINAL_DIRECTORY = os.getcwd()


def change_directory(new_directory):
    os.chdir(new_directory)
    sys.path.append(new_directory)


def start_case_generator():
    change_directory(ORIGINAL_DIRECTORY + "/case_generator/")
    from app import create_app as case_generator__create_app

    case_generator = case_generator__create_app()
    case_generator.run(port=5001, host=CONFIG_DEFAULT_HOST)


def start_toy_ai():
    change_directory(ORIGINAL_DIRECTORY + "/toy_ai/")
    from app import create_app as toy_ai__create_app

    toy_ai = toy_ai__create_app()
    toy_ai.run(port=5002, host=CONFIG_DEFAULT_HOST)


def start_evaluator():
    change_directory(ORIGINAL_DIRECTORY + "/evaluator/")
    from app import create_app as evaluator__create_app

    evaluator = evaluator__create_app()
    evaluator.run(port=5003, host=CONFIG_DEFAULT_HOST)


def start_metric_calculator():
    change_directory(ORIGINAL_DIRECTORY + "/metric_calculator/")
    from app import create_app as metric_calculator__create_app

    metric_calculator = metric_calculator__create_app()
    metric_calculator.run(port=5004, host=CONFIG_DEFAULT_HOST)


def start_simple_ui():
    change_directory(ORIGINAL_DIRECTORY + "/simple_ui/")
    from app import run_app as simple_ui__run_app

    simple_ui__run_app(port=5005, host=CONFIG_DEFAULT_HOST)


def start_participants__babylon_toy_ai():
    change_directory(ORIGINAL_DIRECTORY + "/participants/babylon_toy_ai/")
    from app import create_app as participants__babylon_toy_ai__create_app

    participants__babylon_toy_ai = participants__babylon_toy_ai__create_app()
    participants__babylon_toy_ai.run(port=5006, host=CONFIG_DEFAULT_HOST)


if __name__ == '__main__':
    case_generator = Process(target=start_case_generator)
    case_generator.start()

    toy_ai = Process(target=start_toy_ai)
    toy_ai.start()

    evaluator = Process(target=start_evaluator)
    evaluator.start()

    metric_calculator = Process(target=start_metric_calculator)
    metric_calculator.start()

    simple_ui = Process(target=start_simple_ui)
    simple_ui.start()

    participants__babylon_toy_ai = Process(target=start_participants__babylon_toy_ai)
    participants__babylon_toy_ai.start()
