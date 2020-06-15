from django.utils.decorators import classproperty

from .base import ToyAI
from .utils import solve_case_random_conditions


class UniformRandomConditions(ToyAI):
    @classproperty
    def name(cls) -> str:
        """Returns Toy AI name"""
        return "Uniform Random Conditions Solver"

    @classproperty
    def slug_name(cls) -> str:
        """Returns Toy AI slug"""
        return "uniform-random-conditions"

    @classmethod
    def health_check(cls, *args, **kwargs):
        """Returns Toy AI health check response"""
        return {"data": f"OK from {cls.name}"}

    @classmethod
    def solve_case(cls, payload, *args, **kwargs):
        """Resolves a given case and returns a response with the solution"""
        case_data = payload["caseData"]
        response = {"triage": None, "conditions": []}
        try:
            result = solve_case_random_conditions(case_data, "uniform")
        except Exception as exc:
            response["error"] = f"Error handling case data. Got {str(exc)}"
        else:
            response.update(result)
        return response
