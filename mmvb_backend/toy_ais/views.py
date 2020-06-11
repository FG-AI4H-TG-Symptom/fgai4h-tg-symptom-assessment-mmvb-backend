import json
from http import HTTPStatus

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from toy_ais.implementations import TOY_AIS


# TODO: we will need to protect this view in the future, maybe using JWT?
@method_decorator(csrf_exempt, name="dispatch")
class ToyAIsView(View):
    """View for handling """

    OPERATIONS_MAPPING = {
        "GET": {"health-check": "health_check"},
        "POST": {"solve-case": "solve_case"},
    }
    SLUGS_MAPPING = {ai.slug_name: ai for ai in TOY_AIS}

    def parse_request(self, request, *args, **kwargs):
        """Parses get request for a given toy ai and operation"""
        ai_slug = None
        operation = None
        error = None
        method = request.method

        operation = kwargs.get("operation", None)
        if operation not in self.OPERATIONS_MAPPING[method]:
            error = {
                "message": (
                    f"Operation '{operation}' is invalid. "
                    f"Valid operations are "
                    f"{', '.join(self.OPERATIONS_MAPPING[method])}"
                ),
                "status": HTTPStatus.BAD_REQUEST.value,
            }
        else:
            ai_slug = kwargs.get("ai_slug_name", None)
            if not ai_slug or ai_slug not in self.SLUGS_MAPPING:
                error = {
                    "message": (
                        f"AI with slug name '{ai_slug}' is not implemented. "
                        f"Valid options are {', '.join(self.SLUGS_MAPPING)}"
                    ),
                    "status": HTTPStatus.BAD_REQUEST.value,
                }

        return ai_slug, operation, error

    def parse_post_request(self, request, *args, **kwargs):
        """Parses post request for a given toy ai and operation"""
        payload = {}
        error = None

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError as exc:
            error = {
                "status": HTTPStatus.BAD_REQUEST.value,
                "message": f"Unable to parse payload. Got: {repr(exc)}",
            }

        # TODO: implement data schema validation
        return payload, error

    def get(self, request, *args, **kwargs):
        """Handles get request for a given toy ai and operation"""
        method = request.method
        ai_slug, operation, error = self.parse_request(
            request, *args, **kwargs
        )

        if error is not None:
            status = error["status"]
            data = {"detail": error["message"]}
        else:
            ai = self.SLUGS_MAPPING[ai_slug]
            operation_callable = getattr(
                ai, self.OPERATIONS_MAPPING[method][operation]
            )
            # add try/except
            data = operation_callable()
            status = HTTPStatus.OK.value

        return JsonResponse(data=data, status=status)

    def post(self, request, *args, **kwargs):
        """Handles post request for a given toy ai and operation"""
        method = request.method
        ai_slug, operation, error = self.parse_request(
            request, *args, **kwargs
        )

        if error is not None:
            status = error["status"]
            data = {"detail": status["message"]}
        else:
            payload, error = self.parse_post_request(request, *args, **kwargs)
            if error is not None:
                status = error["status"]
                data = {"detail": status["message"]}
            else:
                ai = self.SLUGS_MAPPING[ai_slug]
                operation_callable = getattr(
                    ai, self.OPERATIONS_MAPPING[method][operation]
                )
                # add try/except
                data = operation_callable(payload)
                status = HTTPStatus.OK.value

        return JsonResponse(data=data, status=status)
