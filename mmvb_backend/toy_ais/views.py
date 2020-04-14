from http import HTTPStatus

from django.http import JsonResponse
from django.views import View

from toy_ais.implementations import TOY_AIS


class ToyAIsView(View):
    OPERATIONS_MAPPING = {
        "health-check": "health_check",
        "solve-case": "solve_case"
    }
    SLUGS_MAPPING = {
        ai.slug_name: ai for ai in TOY_AIS
    }

    def get(self, request, *args, **kwargs):
        data = {}
        status = HTTPStatus.BAD_REQUEST

        operation = kwargs.get("operation", None)
        if operation in self.OPERATIONS_MAPPING:
            ai_slug = kwargs.get("ai_slug_name", None)

            if ai_slug and ai_slug in self.SLUGS_MAPPING:
                ai = self.SLUGS_MAPPING[ai_slug]
                operation_callable = getattr(
                    ai, self.OPERATIONS_MAPPING[operation]
                )
                data = operation_callable()
                status = HTTPStatus.OK
            else:
                data = {
                    "detail": (
                        f"AI with slug name '{ai_slug}' is not implemented. "
                        f"Valid options are {', '.join(self.SLUGS_MAPPING)}"
                    )
                }
        else:
            data = {
                "detail": (
                    f"Operation '{operation}' is invalid. "
                    f"Valid operations are {', '.join(self.OPERATIONS_MAPPING)}"
                )
            }

        return JsonResponse(data=data, status=status)
