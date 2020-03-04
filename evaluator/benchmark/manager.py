import os
import random
from multiprocessing import Pipe, Queue
import queue
import time

from evaluator.benchmark.definitions import ManagerStatuses
from evaluator.benchmark.reporter import create_database_client
from evaluator.benchmark.runner import BenchmarkRunner
from evaluator.benchmark.signals import ProcessSignal
from evaluator.benchmark.utils import create_dirs
from evaluator.constants import MAX_BENCHMARK_RUN_TIME
from logs.logger import get_logger

logger = get_logger()

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname((os.path.abspath(__file__)))), "data"
)


class BenchmarkManager(object):
    """Helper class for managing benchmark executions"""

    def __init__(self, benchmark_start_time):
        self.benchmark_start_time = benchmark_start_time

        try:
            self.benchmark_id
        except AttributeError:
            self.__state = ManagerStatuses.IDLE
            self.db_client = create_database_client()()

    def if_timeout(self):
        return time.time() - self.benchmark_start_time > MAX_BENCHMARK_RUN_TIME

    def setup(self, unique_id, case_set_id, case_set, benchmarked_ais):
        if self.__state == ManagerStatuses.IDLE:
            self.benchmark_id = unique_id
            self.case_set_id = case_set_id
            self.case_set = case_set
            self.accumulated_logs = []
            self.result_queue = Queue()

            self.benchmarked_ais = benchmarked_ais
            self.setup_report()
            self.setup_runners()

            logger.info(
                f"Successfully set up benchmark manager with id {self.benchmark_id} "
                f"for case set with id {self.case_set_id}"
            )
        else:
            raise ValueError

    @property
    def state(self):
        return self.__state

    def setup_report(self):
        self.manager_report = self.db_client.create_manager_report(
            self.benchmark_id, self.case_set_id, len(self.case_set)
        )

    def setup_runners(self):
        if self.__state == ManagerStatuses.IDLE:
            self.runners_pool = []
            ai_names = []
            for index, (ai_name, ai_config) in enumerate(self.benchmarked_ais.items()):
                parent_conn, runner_conn = Pipe()
                runner = BenchmarkRunner(
                    ai_name,
                    ai_config,
                    runner_conn,
                    self.result_queue,
                    index,
                    self.benchmark_start_time,
                )
                ai_names.append(ai_name)
                self.runners_pool.append((runner, parent_conn))
            logger.info(
                f"Sucessfully set up runners for the "
                f'following AIs: {", ".join(ai_names)}'
            )

    def build_report(self):
        report = self.db_client.select_manager_report(self.benchmark_id, prefetch=True)
        report_dict = {
            "benchmark_id": report.benchmark_id,
            "case_set_id": report.case_set_id,
            "total_cases": report.total_cases,
            "current_case_index": report.current_case_index,
            "current_case_id": report.current_case_id,
            "cases": {},
        }
        for ai_report in report.ai_reports:
            case_id = ai_report.case_id
            ai_name = ai_report.ai_name

            if case_id not in report_dict["cases"]:
                report_dict["cases"][case_id] = {}

            if ai_name not in report_dict["cases"][case_id][ai_name]:
                report_dict["cases"][case_id][ai_name] = {
                    "status": ai_report.status,
                    "health_checks": ai_report.health_checks,
                    "errors": ai_report.errors,
                    "soft_timeouts": ai_report.soft_timeouts,
                    "hard_timeouts": ai_report.hard_timeouts,
                }

        return report_dict

    def finish_execution(self):
        self.__state = ManagerStatuses.IDLE
        self.runners_pool = []

    def run_benchmark(self):
        # starts runners
        [runner.start() for runner, _ in self.runners_pool]

        try:
            result = self._run_benchmark()
        finally:
            for (_, pipe) in self.runners_pool:
                pipe.send((ProcessSignal.TERMINATE, None))
                logger.info("Terminating...")
            self.finish_execution()

        return result

    def _run_benchmark(self):
        self.__state = ManagerStatuses.RUNNING
        results = {}
        burnt_cases_path = os.path.join(DATA_DIR, "burnt_cases")
        create_dirs(burnt_cases_path)

        message = f"Starting run of benchmark with id {self.benchmark_id}"
        self.accumulated_logs.append(message)
        logger.info(message)

        for case_num, case in enumerate(self.case_set):
            if self.if_timeout():
                return

            case_index = case_num + 1
            case_id = case["caseData"]["caseId"]
            results[case_id] = {}

            self.manager_report = self.db_client.update_manager_report(
                case_index, case_id, self.manager_report
            )

            runners_pipes = [pipe for (_, pipe) in self.runners_pool]
            random.shuffle(runners_pipes)

            message = f"Starting health checks for case #{case_index}..."
            self.accumulated_logs.append(message)
            logger.info(message)

            for pipe in runners_pipes:
                pipe.send((ProcessSignal.HEALTH_CHECK, {"case_id": case_id}))

            sentinels = 0
            healthchecked_ai_ids = []
            while sentinels < len(self.runners_pool):
                if self.if_timeout():
                    return

                try:
                    signal, runner_id, result = self.result_queue.get(
                        block=True, timeout=1.0
                    )
                except queue.Empty:
                    continue

                if signal == ProcessSignal.SENTINEL:
                    sentinels += 1
                elif signal == ProcessSignal.HEALTH_CHECK:
                    self.db_client.create_ai_report(
                        self.manager_report,
                        result["ai_name"],
                        case_id,
                        result["report"],
                    )
                    if result["healthy"]:
                        healthchecked_ai_ids.append(runner_id)
                    else:
                        # in this case we need to add the failed ai to the results as
                        # not healthchecked successfully
                        output = {
                            "ai_name": result["ai_name"],
                            "result": result["result"],
                            "error": result["error"],
                            "case_status": result["case_status"],
                            "soft_timeout": result["soft_timeout"],
                            "hard_timeout": result["hard_timeout"],
                            "healthchecked": result["healthchecked"],
                        }
                        results[case_id][result["ai_name"]] = output
                    if result["log"]:
                        for log in result["log"]:
                            self.accumulated_logs.append(log)

            if healthchecked_ai_ids:
                message = (
                    "The following AIs have passed the health check for case "
                    + f"#{case_index}: "
                    + ", ".join(
                        [
                            self.runners_pool[id_][0].ai_name
                            for id_ in healthchecked_ai_ids
                        ]
                    )
                )
                self.accumulated_logs.append(message)
                logger.info(message)

                # 'marks' case as 'burnt'
                case_burnt_path = os.path.join(
                    burnt_cases_path, case_id + "_" + str(case_num)
                )
                open(case_burnt_path, "w").close()

            else:
                # if all healthchecks have failed, what to do?
                # TODO: implement rule for when all healthchecks have failed
                message = (
                    f"All AIs have failed the health check for " f"case #{case_index}"
                )
                self.accumulated_logs.append(message)
                logger.error(message)
                return {"runId": self.benchmark_id, "results": results}

            random.shuffle(healthchecked_ai_ids)

            for id_ in healthchecked_ai_ids:
                pipe = self.runners_pool[id_][1]
                pipe.send((ProcessSignal.SOLVE_CASE, {"case": case}))

            sentinels = 0
            while sentinels < len(healthchecked_ai_ids):
                if self.if_timeout():
                    return

                try:
                    signal, runner_id, result = self.result_queue.get(
                        block=True, timeout=1.0
                    )
                except queue.Empty:
                    continue

                if signal == ProcessSignal.SENTINEL:
                    sentinels += 1
                elif signal == ProcessSignal.SOLVE_CASE:
                    logs = result.pop("log")
                    for log in logs:
                        self.accumulated_logs.append(logs)
                    self.db_client.update_ai_report(
                        self.manager_report,
                        result["ai_name"],
                        case_id,
                        case_status=result["case_status"],
                        error=result["error"],
                        soft_timeout=result["soft_timeout"],
                        hard_timeout=result["hard_timeout"],
                    )
                    results[case_id][result["ai_name"]] = result

        message = (
            f"Finished running benchmark with id {self.benchmark_id} "
            f"and case set id {self.case_set_id}"
        )
        self.accumulated_logs.append(message)
        logger.info(message)

        return {"benchmark_id": self.benchmark_id, "results": results}
