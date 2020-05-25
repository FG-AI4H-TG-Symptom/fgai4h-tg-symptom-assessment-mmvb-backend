from concurrent.futures import as_completed
from posixpath import join as urljoin
from uuid import UUID

from django.conf import settings

from benchmarking_sessions.models import (
    BenchmarkingSession,
    BenchmarkingStepError,
    BenchmarkingStepStatus,
)
from celery import shared_task
from requests import ReadTimeout
from requests_futures.sessions import FuturesSession

TIMEOUT = settings.BENCHMARKING_SESSION_TIMEOUT


class BenchmarkReporter:
    def __init__(self, ai_implementations, cases, update_state):
        self.ai_implementations = ai_implementations
        self.cases = cases
        self.update_state = update_state
        self.case_index = None

        self.responses = [
            {
                "caseId": str(case.id),
                "caseIndex": case_index,
                "responses": self.response_template(),
            }
            for case_index, case in enumerate(cases)
        ]

    def response_template(self):
        template = {}

        for ai_implementation in self.ai_implementations:
            template[str(ai_implementation.id)] = {
                "status": BenchmarkingStepStatus.PENDING.value
            }

        return template

    def mark_begin_case(self, case_index):
        self.case_index = case_index

    def _update_case_status(
        self,
        ai_implementation_id: UUID,
        status: BenchmarkingStepStatus,
        error: BenchmarkingStepError = None,
    ):
        response = self.responses[self.case_index]["responses"][
            str(ai_implementation_id)
        ]
        response["status"] = status.value
        if error is not None:
            response["error"] = error.value

        report = {
            "responses": self.responses,
            "statistics": {
                "currentCaseIndex": self.case_index,
                "totalCaseCount": len(self.cases),
            },
        }
        self.update_state(status="PROCESSING", meta=report)

    def processing(self, ai_implementation_id: UUID):
        self._update_case_status(
            ai_implementation_id, BenchmarkingStepStatus.PROCESSING
        )

    def completed(self, ai_implementation_id: UUID, response: dict):
        self._update_case_status(
            ai_implementation_id, BenchmarkingStepStatus.COMPLETED
        )
        self.responses[self.case_index]["responses"][
            str(ai_implementation_id)
        ]["value"] = response

    def error(self, ai_implementation_id: UUID, error: BenchmarkingStepError):
        self._update_case_status(
            ai_implementation_id, BenchmarkingStepStatus.ERRORED, error
        )


@shared_task(bind=True)
def run_benchmark(self, benchmarking_session_id):

    benchmarking_session = BenchmarkingSession.objects.get(
        id=benchmarking_session_id
    )

    benchmarking_session.status = BenchmarkingSession.Status.RUNNING
    benchmarking_session.save()

    case_set = benchmarking_session.case_set
    cases = case_set.cases.all()

    ai_implementations = benchmarking_session.ai_implementations.all()
    reporter = BenchmarkReporter(ai_implementations, cases, self.update_state)

    session = FuturesSession(max_workers=len(ai_implementations))

    for case_index, case in enumerate(cases):
        reporter.mark_begin_case(case_index)

        for ai_implementation in ai_implementations:
            # todo: do health-check
            pass

        request_futures = []
        request_ai_implementation_map = {}

        for ai_implementation in ai_implementations:
            reporter.processing(ai_implementation.id)

            ai_endpoint = urljoin(ai_implementation.base_url, "solve-case")
            request = session.post(
                ai_endpoint,
                json={
                    "caseData": case.data["caseData"],
                    "aiImplementation": ai_implementation.name,
                },
                timeout=TIMEOUT,
            )
            request_futures.append(request)
            request_ai_implementation_map[request] = ai_implementation

        # wait for all to complete
        for request in as_completed(request_futures):
            ai_implementation = request_ai_implementation_map[request]
            request_exception = request.exception(timeout=0)
            if isinstance(request_exception, ReadTimeout):
                reporter.error(
                    ai_implementation.id, BenchmarkingStepError.TIMEOUT
                )
            else:
                response = request.result(timeout=0)
                if not response.ok:
                    reporter.error(
                        ai_implementation.id,
                        BenchmarkingStepError.SERVER_ERROR,
                    )
                    continue

                ai_response = response.json()

                if "error" in ai_response:
                    reporter.error(
                        ai_implementation.id,
                        BenchmarkingStepError.SERVER_ERROR,
                    )
                    continue

                # todo: implement proper validation of response
                if ai_response.get("triage", "") not in [
                    "SC",
                    "PC",
                    "EC",
                    "UNCERTAIN",
                ]:
                    reporter.error(
                        ai_implementation.id,
                        BenchmarkingStepError.BAD_RESPONSE,
                    )
                    continue

                reporter.completed(ai_implementation.id, ai_response)

    benchmarking_session.responses = reporter.responses
    benchmarking_session.status = BenchmarkingSession.Status.FINISHED
    benchmarking_session.save()
