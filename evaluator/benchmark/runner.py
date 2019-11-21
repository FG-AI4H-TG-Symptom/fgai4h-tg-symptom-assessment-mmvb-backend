import json
import os
from multiprocessing import Process
from timeit import default_timer as timer

import requests
from requests.exceptions import ConnectTimeout, Timeout
from retrying import retry

from evaluator.benchmark.definitions import (MAX_NUM_ATTEMPTS,
                                             MAX_WAIT_BETWEEN_RETRIES,
                                             SOLVE_CASE_HARD_TIMEOUT,
                                             SOLVE_CASE_SOFT_TIMEOUT,
                                             CaseStatuses,)
from evaluator.benchmark.exceptions import UnhealthyAIError
from evaluator.benchmark.signals import ProcessSignal
from logs.logger import get_logger

logger = get_logger()


class BenchmarkRunner(Process):
    """
    Helper class to run each step required for a benchmark
    of a given AI
    """

    def __init__(self, ai_name, ai_config, in_pipe, out_queue, runner_id):
        super().__init__()
        self.ai_name = ai_name
        self.runner_id = runner_id
        self.ai_config = ai_config
        self.healthcheck_attempts = 1
        self.solve_case_attempts = 1
        self.in_pipe = in_pipe
        self.out_queue = out_queue

    def run(self):

        signal, parameters = self.in_pipe.recv()

        try:
            while signal is not ProcessSignal.TERMINATE:

                if signal == ProcessSignal.HEALTH_CHECK:
                    self.is_healthy(parameters["case_id"])

                elif signal == ProcessSignal.SOLVE_CASE:
                    solvecase_result = self.solve_case(parameters["case"])
                    self.out_queue.put((signal, self.runner_id, solvecase_result))
                    self.out_queue.put((ProcessSignal.SENTINEL, self.runner_id, None))

                elif signal == ProcessSignal.SENTINEL:
                    raise ValueError(f"Unexpected signal {signal} received")

                signal, parameters = self.in_pipe.recv()
        finally:
            self.out_queue.put(
                (
                    ProcessSignal.SENTINEL,
                    self.runner_id,
                    {"ai_name": self.ai_name, "results": {}},
                )
            )
        return

    def _perform_request(
        self, url, method="GET", parameters=None, data=None, timeout=3, headers=None
    ):
        parameters = parameters or {}
        data = data or {}
        headers = headers or {}

        response = requests.request(
            method,
            url,
            params=parameters,
            data=json.dumps(data),
            headers=headers,
            timeout=timeout,
        )
        return response

    def _update_attempts(self):
        if self.healthcheck_attempts >= MAX_NUM_ATTEMPTS:
            self.healthcheck_attempts = 1
            return False

        self.healthcheck_attempts += 1
        return True

    def _log_error(self, message=None, status_code=None, data=None, exception=None):
        if not message:
            message = (
                f"Max attempts of {MAX_NUM_ATTEMPTS} retries failed "
                f"for {self.ai_name}."
            )

            data = data or {}
            if exception:
                message += f" Got {str(exception)}"
            elif status_code:
                message += f" Got status code {status_code}"
                if data:
                    message += f" and data={data}"

        logger.error(message)

    def _log_info(self, message=None, status_code=None, data=None, exception=None):
        if not message:
            message = (
                f"Health check attempt #{self.healthcheck_attempts} failed "
                f"for {self.ai_name}."
            )

            data = data or {}
            if exception:
                message += f" Got {str(exception)} but should retry soon..."
            elif status_code:
                message += f" Got status code {status_code}"
                if data:
                    message += f" and data={data}"

        logger.info(message)

    def _respond_healthcheck_signal(self, result, send_sentinel=False):
        self.out_queue.put((ProcessSignal.HEALTH_CHECK, self.runner_id, result))

        if send_sentinel:
            self.out_queue.put((ProcessSignal.SENTINEL, self.runner_id, None))

    @retry(
        stop_max_attempt_number=MAX_NUM_ATTEMPTS,
        wait_exponential_multiplier=50,
        wait_exponential_max=MAX_WAIT_BETWEEN_RETRIES * 1000,
    )
    def is_healthy(self, case_id):

        result = {
            "ai_name": self.ai_name,
            "result": {},
            "healthy": False,
            "error": None,
            "case_status": CaseStatuses.ERROR,
            "soft_timeout": False,
            "hard_timeout": False,
            "healthchecked": False,
            "report": {
                "health_checks": 1,
                "healthcheck_status": CaseStatuses.RUNNING,
                "errors": 0,
                "soft_timeouts": 0,
                "hard_timeouts": 0,
            },
            "log": [],
        }

        healthcheck_endpoint = self.ai_config["health_check"]

        try:
            response = self._perform_request(
                healthcheck_endpoint,
                method="POST",
                data={"aiImplementation": self.ai_name},
                headers={"Content-Type": "application/json"},
            )
        except Exception as exc:
            should_retry = self._update_attempts()
            if should_retry:
                self._log_info(exception=exc)
                result["log"].append(
                    f"Failed healthcheck #{self.healthcheck_attempts - 1} "
                    f"for AI {self.ai_name}. Retrying..."
                )
                self._respond_healthcheck_signal(result)
                raise
            else:
                result["report"]["errors"] = 1
                result["report"]["healthcheck_status"] = CaseStatuses.ERROR
                result["log"].append(
                    f"Error on healthcheck #{self.healthcheck_attempts} "
                    f"for AI {self.ai_name}. Got {str(exc)}"
                )
                self._log_error(exception=exc)
                self._respond_healthcheck_signal(result, send_sentinel=True)
        else:
            if response.status_code != 200:
                should_retry = self._update_attempts()

                if should_retry:
                    self._log_info(
                        status_code=response.status_code, data=response.json()
                    )
                    self._respond_healthcheck_signal(result)
                    result["log"].append(
                        f"Unhealthy response on healthcheck "
                        f"#{self.healthcheck_attempts - 1} for "
                        f"{self.ai_name}. Retrying..."
                    )
                    raise UnhealthyAIError(
                        f"Retrying health check for {self.ai_name} after bad "
                        f"status code..."
                    )
                else:
                    result["report"]["errors"] = 1
                    result["report"]["healthcheck_status"] = CaseStatuses.ERROR
                    result["log"].append(
                        f"Error: could not get successful healthcheck response for "
                        f"{self.ai_name} after {MAX_NUM_ATTEMPTS} attempts."
                    )
                    self._log_error(
                        status_code=response.status_code, data=response.json()
                    )
                    self._respond_healthcheck_signal(result, send_sentinel=True)
            else:
                data = response.json()
                if data.get("status", "Error") != "OK":
                    should_retry = self._update_attempts()
                    if should_retry:
                        self._log_info(status_code=response.status_code, data=data)
                        self._respond_healthcheck_signal(result)
                        result["log"].append(
                            f"Unhealthy response on healthcheck "
                            f"#{self.healthcheck_attempts - 1} for {self.ai_name}. "
                            f"Retrying..."
                        )
                        raise UnhealthyAIError(
                            f"Retrying health check for {self.ai_name} "
                            f"after bad response data..."
                        )
                    else:
                        result["report"]["errors"] = 1
                        result["report"]["healthcheck_status"] = CaseStatuses.ERROR
                        result["log"].append(
                            f"Error: could not get successful healthcheck response for "
                            f"{self.ai_name} after {MAX_NUM_ATTEMPTS} attempts."
                        )
                        self._log_error(
                            status_code=response.status_code, data=response.json()
                        )
                        self._respond_healthcheck_signal(result, send_sentinel=True)

                else:
                    message = (
                        f"Successful health check for {self.ai_name} on "
                        f"attempt #{self.healthcheck_attempts}"
                    )
                    result["log"].append(message)
                    self._log_info(message=message)
                    result["healthy"] = True
                    result["report"]["healthcheck_status"] = CaseStatuses.OK
                    self._respond_healthcheck_signal(result, send_sentinel=True)

    def solve_case(self, case):

        return_dict = {
            "ai_name": self.ai_name,
            "result": {},
            "error": None,
            "case_status": CaseStatuses.RUNNING,
            "healthchecked": True,
            "soft_timeout": False,
            "hard_timeout": False,
            "log": [],
        }

        case_data = case["caseData"]

        solve_case_endpoint = self.ai_config["solve_case"]

        data = {"caseData": case_data, "aiImplementation": self.ai_name}

        message = f"Starting call to solve-case endpoint of AI {self.ai_name}"
        return_dict["log"].append(message)
        self._log_info(message)
        try:
            start = timer()
            response = self._perform_request(
                solve_case_endpoint,
                method="POST",
                data=data,
                timeout=SOLVE_CASE_HARD_TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
            end = timer()
        except (Timeout, ConnectTimeout) as exc:
            return_dict["error"] = str(exc)
            return_dict["case_status"] = CaseStatuses.ERROR
            return_dict["hard_timeout"] = True
            message = (
                f"Hard timeout ({SOLVE_CASE_HARD_TIMEOUT}sec) "
                f"solving case for {self.ai_name}"
            )
            return_dict["log"].append(message)
            self._log_error(message=message)
        except Exception as exc:
            return_dict["error"] = str(exc)
            return_dict["case_status"] = CaseStatuses.ERROR
            message = f"Error solving case for {self.ai_name}. Got {str(exc)}"

            return_dict["log"].append(message)
            self._log_error(message=message)
        else:
            elapsed_time = end - start
            if elapsed_time > SOLVE_CASE_SOFT_TIMEOUT:
                return_dict["soft_timeout"] = True
                message = (
                    f"Soft timeout ({SOLVE_CASE_SOFT_TIMEOUT}sec) "
                    f"solving case for {self.ai_name}"
                )

                return_dict["log"].append(message)
                self._log_info(message=message)

            if response.status_code != 200:
                message = (
                    f"AI {self.ai_name} responded with unexpected HTTP "
                    f"status {response.status_code} and data={response}"
                )
                return_dict["error"] = message
                return_dict["case_status"] = CaseStatuses.ERROR

                return_dict["log"].append(message)
                self._log_error(message=message)
            else:
                return_dict["result"] = response.json()
                return_dict["case_status"] = CaseStatuses.OK
                message = (
                    f"Successfuly called solve-case endpoint of AI "
                    f"{self.ai_name}. Took {elapsed_time:.1f}sec"
                )
                self._log_info(message=message)

        return return_dict
